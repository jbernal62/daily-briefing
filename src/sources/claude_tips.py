"""Claude Code daily tips — rotating list of useful tricks."""

import hashlib
from datetime import datetime, timezone

CLAUDE_CODE_TIPS = [
    {
        "title": "Use /compact to save context window",
        "tip": "When your conversation gets long, type /compact to compress the history. Claude keeps working but uses fewer tokens. Essential for long coding sessions."
    },
    {
        "title": "Vim mode: Ctrl+Shift+V to toggle",
        "tip": "Enable vim keybindings in Claude Code for faster text editing. Navigate with hjkl, use dd to delete lines, and yy to yank."
    },
    {
        "title": "Multi-file edits with Task tool",
        "tip": "Use Claude Code's Task tool to dispatch subagents for parallel work. Each agent gets its own context, perfect for editing multiple files at once."
    },
    {
        "title": "Use @ to reference files in prompts",
        "tip": "Type @filename to directly reference files in your prompt. Claude will read them automatically without you needing to paste content."
    },
    {
        "title": "Custom slash commands in CLAUDE.md",
        "tip": "Define custom workflows in your project's CLAUDE.md file. Add instructions that Claude follows automatically when working in your repo."
    },
    {
        "title": "Hooks: automate pre/post tool actions",
        "tip": "Configure hooks in ~/.claude/settings.json to run shell commands before or after tool calls. Auto-format on save, auto-lint on edit."
    },
    {
        "title": "Use --resume to continue sessions",
        "tip": "Run 'claude --resume' to pick up where you left off in a previous session. Your full context and conversation history are preserved."
    },
    {
        "title": "Pipe output directly to Claude",
        "tip": "Use 'cat error.log | claude \"explain this error\"' to pipe any output directly into Claude Code for analysis."
    },
    {
        "title": "MCP servers extend Claude's capabilities",
        "tip": "Add MCP servers in settings to give Claude access to databases, APIs, browsers, and more. Each server provides specialized tools."
    },
    {
        "title": "Use /init to bootstrap a project CLAUDE.md",
        "tip": "Run /init in a new project to have Claude analyze your codebase and generate a tailored CLAUDE.md with project conventions and instructions."
    },
    {
        "title": "Git worktrees for isolated feature work",
        "tip": "Use git worktrees to work on features in isolation. Claude can manage multiple worktrees, each with its own branch and working directory."
    },
    {
        "title": "Subagents for parallel research",
        "tip": "Dispatch Explore subagents to research multiple questions simultaneously. Each gets its own context and returns findings to the main conversation."
    },
    {
        "title": "Use --print for non-interactive mode",
        "tip": "Run 'claude --print \"question\"' for a single-shot answer without entering interactive mode. Perfect for quick lookups and scripting."
    },
    {
        "title": "TodoWrite for progress tracking",
        "tip": "Use the TodoWrite tool to create visible task lists. Helps track complex multi-step work and shows progress to the user in real-time."
    },
    {
        "title": "Glob + Grep before Read",
        "tip": "Search with Glob and Grep first to find the right files, then Read only what you need. Saves tokens and finds code faster than reading everything."
    },
    {
        "title": "Permission modes control autonomy",
        "tip": "Set Claude Code to 'plan' mode for cautious work, or 'auto' mode for autonomous execution. Match the mode to your trust level and task risk."
    },
    {
        "title": "Memory files persist across sessions",
        "tip": "Write key learnings to ~/.claude/projects/*/memory/ files. They're loaded into every new session's system prompt for continuity."
    },
    {
        "title": "Use WebSearch for current info",
        "tip": "Claude Code can search the web for up-to-date information. Use it for docs, pricing, latest releases, and anything beyond the training cutoff."
    },
    {
        "title": "Edit tool over sed/awk",
        "tip": "Always use Claude's Edit tool instead of shell commands for file modifications. It's safer, reversible, and shows the user exactly what changed."
    },
    {
        "title": "Parallel tool calls for speed",
        "tip": "Claude can call multiple independent tools in one response. Reading 3 files? They all execute in parallel, dramatically faster than sequential reads."
    },
    {
        "title": "Skills add specialized workflows",
        "tip": "Install Claude Code plugins/skills for TDD, debugging, code review, and more. Skills enforce best practices and structured workflows."
    },
    {
        "title": "Use EnterPlanMode for complex tasks",
        "tip": "For multi-file features, call EnterPlanMode first. Claude explores the codebase, designs the approach, and gets your approval before writing code."
    },
    {
        "title": "AskUserQuestion for clarity",
        "tip": "When requirements are ambiguous, Claude can present multiple-choice questions. Faster than typing explanations and prevents wrong assumptions."
    },
    {
        "title": "NotebookEdit for Jupyter work",
        "tip": "Claude can read, edit, and create Jupyter notebook cells directly. Use it for data science workflows without leaving the CLI."
    },
    {
        "title": "Background tasks with run_in_background",
        "tip": "Long-running commands can be dispatched to the background. Claude continues working while builds, tests, or deploys run asynchronously."
    },
    {
        "title": "HEREDOC for multi-line git commits",
        "tip": "Claude uses HEREDOC syntax for commit messages to preserve formatting. Multi-line messages with proper structure, every time."
    },
    {
        "title": "Episodic memory searches past sessions",
        "tip": "Use the episodic-memory skill to search previous conversation history. Recover decisions, solutions, and lessons from past coding sessions."
    },
    {
        "title": "Read tool supports images and PDFs",
        "tip": "Claude Code is multimodal — it can view screenshots, diagrams, and read PDFs directly. Share a screenshot of a bug and Claude analyzes it visually."
    },
    {
        "title": "Chain commands with && in Bash",
        "tip": "For dependent operations, chain with &&: 'git add . && git commit -m msg && git push'. Each step only runs if the previous succeeded."
    },
    {
        "title": "Use gh CLI for GitHub operations",
        "tip": "Claude uses 'gh' for all GitHub work — PRs, issues, checks, releases. Faster and more reliable than web-based GitHub interactions."
    },
]


def get_daily_tip() -> list[dict]:
    """Get today's Claude Code tip based on date."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    # Deterministic daily rotation based on date hash
    idx = int(hashlib.md5(today.encode()).hexdigest(), 16) % len(CLAUDE_CODE_TIPS)
    tip = CLAUDE_CODE_TIPS[idx]

    return [{
        "category": "claude_tip",
        "title": f"Claude Code Tip: {tip['title']}",
        "description": tip["tip"],
        "source": "Claude Code Tips",
        "url": "https://docs.anthropic.com/en/docs/claude-code",
        "published": today,
    }]
