from google.transit import gtfs_realtime_pb2
from dataclasses import dataclass
from typing import Dict, Any, Optional
import time
import aiohttp
from google.transit import gtfs_realtime_pb2

# Data structure to hold fetched RT feed data
@dataclass
class RTFeed:
    fetched_at: float
    header_ts: Optional[int]
    entities: Dict[str, Any] # key: trip_id or vehicle_id

# Real-time GTFS feed client
class RTClient:
    def __init__(self, session: aiohttp.ClientSession):
        self.session = session

    # feed fetcher
    async def fetch_feed(self, url: str, headers: Dict[str, str], timeout_s: int = 10) -> bytes:
        async with self.session.get(url, headers=headers, timeout=timeout_s) as response:
            response.raise_for_status()
            return await response.read()

    # Fetchs trip updates from feed
    async def fetch_trip_updates(self, url: str, headers: Dict[str, str]) -> RTFeed:
        # Fetch raw feed data
        raw = await self.fetch_feed(url, headers=headers)
        msg = gtfs_realtime_pb2.FeedMessage()
        msg.ParseFromString(raw)

        # Parse trip updates
        out: Dict[str, Any] = {}
        for ent in msg.entity:
            if not ent.trip_update or not ent.trip_update.trip.trip_id:
                continue
        
            # Extract trip update details
            trip_id = ent.trip_update.trip.trip_id
            stus = []

            # Extract stop time updates
            for stu in ent.trip_update.stop_time_update:
                stus.append({
                    "stop_id": stu.stop_id,
                    "arr_delay": stu.arrival.delay if stu.HasField("arrival") else None,
                    "arr_time":  stu.arrival.time  if stu.HasField("arrival") else None,
                    "dep_delay": stu.departure.delay if stu.HasField("departure") else None,
                    "dep_time":  stu.departure.time  if stu.HasField("departure") else None,
                })
            
            # Store trip update info
            out[trip_id] = {
                "route_id": ent.trip_update.trip.route_id or None,
                "timestamp": ent.trip_update.timestamp or None,
                "stop_time_updates": stus,
            }

        # Extract header timestamp
        header_ts = msg.header.timestamp if msg.header and msg.header.timestamp else None
        return RTFeed(fetched_at=time.time(), header_ts=header_ts, entities=out)

    # Fetchs vehicle positions from feed
    async def fetch_vehicle_positions(self, url: str, headers: Dict[str, str]) -> RTFeed:
        # Fetch raw feed data
        raw = await self.fetch_feed(url, headers=headers)
        msg = gtfs_realtime_pb2.FeedMessage()
        msg.ParseFromString(raw)

        # Parse vehicle positions
        out: Dict[str, Any] = {}
        for ent in msg.entity:
            if not ent.vehicle:
                continue
            
            # Extract vehicle position details
            trip_id = ent.vehicle.trip.trip_id if ent.vehicle.trip and ent.vehicle.trip.trip_id else None
            vehicle_id = ent.vehicle.vehicle.id if ent.vehicle.vehicle and ent.vehicle.vehicle.id else None
            key = trip_id or vehicle_id
            if not key:
                continue
            
            # Extract position info
            pos = ent.vehicle.position
            out[key] = {
                "trip_id": trip_id,
                "route_id": ent.vehicle.trip.route_id if ent.vehicle.trip else None,
                "timestamp": ent.vehicle.timestamp or None,
                "lat": pos.latitude if pos and pos.HasField("latitude") else None,
                "lon": pos.longitude if pos and pos.HasField("longitude") else None,
                "bearing": pos.bearing if pos and pos.HasField("bearing") else None,
            }

        # Extract header timestamp
        header_ts = msg.header.timestamp if msg.header and msg.header.timestamp else None
        return RTFeed(fetched_at=time.time(), header_ts=header_ts, entities=out)