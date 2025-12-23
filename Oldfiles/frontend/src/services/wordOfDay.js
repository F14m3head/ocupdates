export default async function getWordOfDay() {
    try {
        const res = await fetch("http://127.0.0.1:8000/word-of-day"); // TODO: use .env file to get backend URL
        
        if(!res.ok) throw new Error("Failed to fetch word of day.");

        return await res.json();
    } catch {
        throw new Error("Failed to fetch word of day.");
    }
}