// bot.ts
import { Client, GatewayIntentBits, TextChannel } from "discord.js";
import { spawn } from "child_process";
import dotenv from "dotenv";

dotenv.config();

const client = new Client({
    intents: [GatewayIntentBits.Guilds, GatewayIntentBits.GuildMessages, GatewayIntentBits.MessageContent]
});

client.once("ready", () => {
    console.log(`Logged in as ${client.user?.tag}`);
});

client.on("messageCreate", async (message) => {
    if (message.content === "!updates") {
        const python = spawn("python3", ["parser.py"]);

        let data = "";

        python.stdout.on("data", (chunk) => {
            data += chunk.toString();
        });

        python.stderr.on("data", (err) => {
            console.error("Python error:", err.toString());
            message.channel.send("There was an error fetching updates.");
        });

        python.on("close", () => {
            try {
                const updates = JSON.parse(data);

                if (updates.length === 0) {
                    message.channel.send("No service updates available.");
                    return;
                }

                for (const update of updates) {
                    message.channel.send(`**${update.title}**\n${update.published}\n${update.link}`);
                }
            } catch (err) {
                console.error("Failed to parse output:", err);
                message.channel.send("Failed to parse update data.");
            }
        });
    }
});

client.login(process.env.BOT_TOKEN);
