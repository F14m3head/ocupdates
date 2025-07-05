# 🗺️ ocUpdates Feature Roadmap

## 🚦 Phase 1: Status updates
Base features to get used to data format and implement service updates

### ❗Status Updates 
- [ ] Show **detours** with estimated duration until resolved
  - [ ] Show original routing
  - [ ] Show modified routing
  - [ ] Show expected delay in minutes
  - [ ] Show anticipated resolution date
  - [ ] Identify affected routes and directions
  - [ ] Use some sort of engine to display detour and original routing
- [ ] Display **route cancellations** by trip number
  - [ ] Display time of cancelled trip
  - [ ] Display route number and direction
  - [ ] Display next available scheduled departure
- [ ] Highlight **station maintenance** events
  - [ ] Identify affected station
  - [ ] identify affected services
  - [ ] Provide explanation as to reason of maintenance
  - [ ] Provide anticipâted resolution date
- [ ] Notify of **delays**, with estimated arrivals for affected trips (when data available)
  - [ ] Display route number and direction
  - [ ] Display trip id
  - [ ] Display estimated arrival of trip

### ☁️ Cloud intergrations
- [ ] Discord bot
  - [ ] Integrate status updates
  - [ ] Create notifications
- [ ] Website
  - [ ] Create UI (must have a dark mode option)
  - [ ] Create FAQ
  - [ ] Create contact page
  - [ ] Create landing page
  - [ ] Create working status updates page
  - [ ] Intergrate detour engine with interactive map

## 🚧 Phase 2: Trip planning
Base trip planning features with real-time updates

### 🧭 Trip Planning  
- [ ] Enable **route filtering** to avoid certain routes
  - [ ] Enable removal of specified routes from parsed data
  - [ ] Remove affected trips from displayed options to user
  - [ ] Add toggle to show hidden trips
- [ ] Display **estimated ETA and fare costs**, with fare window breakdowns
  - [ ] Show user estimated total cost of trip
  - [ ] Show user total transfer usage time
  - [ ] Show user fare paid zones if they access them on their trip
  - [ ] Display estimated time of arrival
  - [ ] Display different routings for a selected destination from a selected origin
- [ ] Show **real-time bus positions** across multiple routes
  - [ ] Use some sort of engine to display and dynamically update bus positions
  - [ ] Add toggle for dynamic updates (to save bandwidth)
- [ ] Use algorithms to remove redundant trip suggestions
  - [ ] Remove transfers to different routes when they have the same routing for the remainder of their trips

### ☁️ Cloud intergrations
- [ ] Website
  - [ ] Create trip planning page
  - [ ] Integrate algorithms

## 🚧 Phase 3: Personalization & Routing Intelligence
More advanced trip planning 

### 🧠 Smart Trip Planning
- [ ] Adjust **minimum and maximum transfer times**
  - [ ] Allow user to set preferred transfer lengths
- [ ] Allow users to **set preferred routes**
  - [ ] Allow favorite/quick access routes
  - [ ] View detours/cancellations/late arrivals
- [ ] Allow users to **set favorite destinations**
  - [ ] Allow favorite/quick access locations
- [ ] Customize **walking and cycling speeds** for accurate travel time
  - [ ] Allow custom speeds for each transfer?

### ☁️ Cloud intergrations
- [ ] Website
  - [ ] Allow profile creation for saved preferences

## 🌟 Phase 4: Route ratings & Advanced Features
Pinnacle features

### 📍 Trip planning
- [ ] Support **multi-destination trips**, each with customizable arrival and departure times
  - [ ] Allow trip planning with multiple destinations without compromising on features

### 📊 Route ratings
- [ ] Show **route reliability** and **trip scores** based on community feedback
  - [ ] Use GO crowdsourcing to obtain data
     
### ☁️ Cloud intergrations
- [ ] Website
  - [ ] Intergrate ratings

## 📅 Optional Future Enhancements
(For after core development or based on user demand)
- [ ] Offline trip planning mode
  - [ ] Save offline maps and use gps for accurate positionning
  - [ ] Bake routes into maps
  - [ ] Use interactive maps
