// landing/app.js

// 1. Click to Copy Installer Command
function copyInstallCommand() {
    const cmdText = document.getElementById("cmdText").innerText;
    navigator.clipboard.writeText(cmdText).then(() => {
        const feedback = document.getElementById("copyFeedback");
        const copyBtn = document.getElementById("copyBtn");
        
        feedback.classList.add("show");
        copyBtn.innerText = "Copied!";
        
        setTimeout(() => {
            feedback.classList.remove("show");
            copyBtn.innerText = "Copy";
        }, 2000);
    }).catch(err => {
        console.error("Failed to copy command: ", err);
    });
}

// 2. Terminal Script Definitions
const TERMINAL_SCRIPTS = {
    1: [
        { type: "input", text: "secapi check ." },
        { type: "output", delay: 400, text: "\n🔍 Scanning directory: .\n" },
        { type: "output", delay: 200, text: "<span class='term-red term-bold'>[1] Stripe</span> in <span class='term-cyan'>./demo_project/main.py</span> (line 4)\n" },
        { type: "output", delay: 100, text: "    stripe_key = <span class='term-yellow'>\"sk_live_51Nz" + "ABCDeFGHIJKLMNOPQRST\"</span> # Don't leak this!\n\n" },
        { type: "output", delay: 300, text: "<span class='term-red term-bold'>❌ Scan failed:</span> Found 1 potential secret(s).\n" }
    ],
    2: [
        { type: "input", text: "secapi add" },
        { type: "output", delay: 400, text: "\n🔐 Setting up secure local vault...\n" },
        { type: "output", delay: 300, text: "🔑 Enter master password: <span class='term-gray'>********</span>\n" },
        { type: "output", delay: 200, text: "🔑 Confirm master password: <span class='term-gray'>********</span>\n\n" },
        { type: "output", delay: 400, text: "<span class='term-yellow term-bold'>👉 EMERGENCY RECOVERY MNEMONIC:</span>\n" },
        { type: "output", delay: 100, text: "<span class='term-yellow term-bold'>👉  SILK-PATH-IRON-FORT-WOLF-HAWK  👈</span>\n" },
        { type: "output", delay: 100, text: "<span class='term-gray'>(Write this down! It is your only recovery option.)</span>\n\n" },
        { type: "output", delay: 450, text: "Key name: stripe_key\n" },
        { type: "output", delay: 200, text: "Enter API key: <span class='term-gray'>*********************************</span>\n\n" },
        { type: "output", delay: 300, text: "<span class='term-green term-bold'>✅ Replaced and stored key 'stripe_key' securely.</span>\n" }
    ],
    3: [
        { type: "input", text: "cat demo_project/main.py" },
        { type: "output", delay: 500, text: "\n<span class='term-cyan'>from</span> secapi.secure <span class='term-cyan'>import</span> load_key\n" },
        { type: "output", delay: 50, text: "<span class='term-cyan'>import</span> os\n\n" },
        { type: "output", delay: 50, text: "<span class='term-gray'># A typical application containing a hardcoded API key</span>\n" },
        { type: "output", delay: 50, text: "stripe_key = load_key(<span class='term-green'>\"stripe_key\"</span>) <span class='term-gray'># Don't leak this!</span>\n" },
        { type: "output", delay: 50, text: "print(<span class='term-yellow'>f\"Connecting to Stripe...\"</span>)\n" }
    ],
    4: [
        { type: "input", text: "secapi list" },
        { type: "output", delay: 400, text: "\n============================================================\n" },
        { type: "output", delay: 50, text: "                    <span class='term-bold term-cyan'>SECAPI KEY MANAGER</span>\n" },
        { type: "output", delay: 50, text: "============================================================\n" },
        { type: "output", delay: 50, text: "KEY NAME            STATUS         AGE (DAYS)    CREATED AT\n" },
        { type: "output", delay: 50, text: "------------------------------------------------------------\n" },
        { type: "output", delay: 50, text: "stripe_key          <span class='term-green'>🟢 ACTIVE</span>      0             2026-05-30\n" },
        { type: "output", delay: 50, text: "openai_key          <span class='term-yellow'>🟡 ROTATE DUE</span>  28            2026-05-02\n" },
        { type: "output", delay: 50, text: "aws_access_key      <span class='term-red'>🔴 EXPIRED</span>     95            2026-02-24\n" },
        { type: "output", delay: 50, text: "============================================================\n" }
    ],
    5: [
        { type: "input", text: "secapi init-hook" },
        { type: "output", delay: 400, text: "\n📦 Registering git pre-commit hook...\n" },
        { type: "output", delay: 300, text: "<span class='term-green term-bold'>✅ Installed pre-commit hook in .git/hooks/pre-commit</span>\n\n" },
        { type: "output", delay: 500, text: "<span class='term-prompt'>user@dev:~/my_project$</span> git commit -m \"add payment integration\"\n" },
        { type: "output", delay: 400, text: "🔍 Running SecAPI Pre-commit Hook...\n" },
        { type: "output", delay: 200, text: "<span class='term-red term-bold'>❌ Blocked:</span> Found unencrypted secret in gateway.py line 12!\n" },
        { type: "output", delay: 100, text: "<span class='term-yellow'>Please vault it using 'secapi check' before committing.</span>\n" }
    ]
};

// 3. Interactive Terminal Engine
class TerminalSimulator {
    constructor(elementId) {
        this.container = document.getElementById(elementId);
        this.activeTimers = [];
        this.currentStep = 0;
    }

    clear() {
        this.activeTimers.forEach(clearTimeout);
        this.activeTimers = [];
        this.container.innerHTML = "";
    }

    writeLine(html, className = "") {
        const div = document.createElement("div");
        if (className) div.className = className;
        div.innerHTML = html;
        this.container.appendChild(div);
        this.container.scrollTop = this.container.scrollHeight;
    }

    playScript(stepIndex) {
        if (this.currentStep === stepIndex) return; // Prevent double execution
        this.currentStep = stepIndex;
        this.clear();

        const script = TERMINAL_SCRIPTS[stepIndex];
        if (!script) return;

        let totalDelay = 0;

        script.forEach((action) => {
            if (action.type === "input") {
                // Add command prompt line
                const promptId = "prompt-" + Math.random().toString(36).substr(2, 9);
                const inputId = "input-" + Math.random().toString(36).substr(2, 9);

                this.writeLine(`<span class="term-prompt">user@dev:~/my_project$</span> <span id="${inputId}"></span><span class="term-cursor" id="cursor-${inputId}"></span>`, "prompt-line");

                const chars = action.text.split("");
                chars.forEach((char, charIdx) => {
                    const timer = setTimeout(() => {
                        const target = document.getElementById(inputId);
                        if (target) target.innerHTML += char;
                    }, totalDelay + (charIdx * 45));
                    this.activeTimers.push(timer);
                });

                totalDelay += (chars.length * 45) + 300; // Pause after typing
                
                // Hide prompt cursor when typing finishes
                const hideCursorTimer = setTimeout(() => {
                    const cursor = document.getElementById(`cursor-${inputId}`);
                    if (cursor) cursor.style.display = "none";
                }, totalDelay - 100);
                this.activeTimers.push(hideCursorTimer);

            } else if (action.type === "output") {
                totalDelay += action.delay;
                const timer = setTimeout(() => {
                    this.writeLine(action.text);
                }, totalDelay);
                this.activeTimers.push(timer);
            }
        });
    }
}

// 4. Initialize Scrollytelling & Observers
document.addEventListener("DOMContentLoaded", () => {
    const term = new TerminalSimulator("terminalOutput");
    
    // Play initial greeting
    term.writeLine("SecAPI Local Session v0.1.0 ready.");
    term.writeLine("<span class='term-gray'>Scroll down the features list to see how it works...</span>\n");
    term.writeLine("<span class='term-prompt'>user@dev:~/my_project$</span> <span class='term-cursor'></span>");

    // Intersection Observer for Step Cards
    const stepCards = document.querySelectorAll(".step-card");
    const observerOptions = {
        root: null,
        rootMargin: "-25% 0px -40% 0px", // Trigger when step is centered in viewport
        threshold: 0.2
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                // Remove active class from all
                stepCards.forEach(card => card.classList.remove("active"));
                
                // Set active to current
                entry.target.classList.add("active");
                
                const stepNum = parseInt(entry.target.getAttribute("data-step"));
                term.playScript(stepNum);
            }
        });
    }, observerOptions);

    stepCards.forEach(card => observer.observe(card));
});
