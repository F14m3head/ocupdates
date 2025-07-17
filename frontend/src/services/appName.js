export default async function getAppName() {
    try {
        //const res = await fetch('http://127.0.0.1:8000/app-name');  // TODO: use .env file to get backend URL
        
        //if(!res.ok) throw new Error("Failed to fetch app name.");

        //return await res.json();
        return { appName: "ocUpdates" };
    } catch {
        throw new Error("Failed to fetch app name.");
    }
}