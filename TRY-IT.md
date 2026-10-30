# Try the agent team yourself

A step-by-step test, so nothing real is touched. For a normal chat, go straight to Part 7. About 30 minutes and about $1 of usage for both tasks. Nothing goes out: everything stays on your computer.

## Before you start
- The Claude desktop app, with the **Code** tab.
- Access to the GitHub repository **Dolat-Hamza/geevs-ai-skills**. Sign in to GitHub if asked.
- Optional: type `/usage` in Claude before and after, to see the usage.

## Part 1: Install it (once)
1. In the Claude app, open the **Code** tab and start a new session (any folder). Paste and send:
   > Please install the agent team plugin by running these two commands: claude plugin marketplace add Dolat-Hamza/geevs-ai-skills and then claude plugin install geevs-agent-team@geevs
2. **Quit the Claude app completely and open it again.**

## Part 2: Get the practice project
1. In a Code session, paste:
   > Copy the folder examples/practice-project from the GitHub repository Dolat-Hamza/geevs-ai-skills into a new folder on my Desktop called agent-practice. Then make agent-practice its own git repository with one commit.
2. Start a **new Code session** and choose the **agent-practice** folder. Say yes if asked to trust it. The safety rules only apply when the session is opened inside the project's own folder.

## Part 3: Switch it on for this project
Type `/geevs-agent-team:setup`. Claude confirms the safety rules were added: it now asks you before pushing, merging, deploying or publishing anything in this folder.

## Part 4: First task, write a customer note
1. Type:
   > /geevs-agent-team:deliver Write a one-paragraph customer note explaining the minimum fee and rounding rule, with one worked example, citing the README.
2. Answer its questions. For example: retail customers; only the README price list; done means every figure is checked against the price list.
3. Read the plan (a short checklist). Ask for changes in plain words if you want any, then reply **approved**.
4. Wait a few minutes while one team member writes it and a separate one checks every figure.
5. Read the summary. Try asking "Show me the note" or "How did you check the figures?"

## Part 5: Second task, fix the pricing mistake
1. Type:
   > /geevs-agent-team:deliver Transfers of exactly 1,000 and exactly 10,000 GBP are charged the wrong fee. Fix it so the fees match the pricing table in the README.
2. Answer its questions, read the plan, reply **approved**.
3. The fix is made on a separate copy, and the team proves it: new checks fail on the old version and pass on the fixed one.
4. In the summary, £1,000 should now cost £5.00 instead of £10.00, and £10,000 should cost £25.00 instead of £50.00.

## Part 6: Try something of your own
Use a copy of a real project folder. Repeat Part 3 there, then type `/geevs-agent-team:deliver` followed by what you want.

## Part 7: Use it in a normal chat
Doesn't need Parts 1 to 6.
1. Signed in to GitHub, open https://github.com/Dolat-Hamza/geevs-ai-skills/raw/master/dist/geevs-agent-team.zip. Don't unzip it.
2. In Claude: **Customize → Plugins → Add → Upload plugin**, pick **geevs-agent-team.zip**. Its Skills tab shows **deliver** and **setup**.
3. **Settings → Capabilities**: **Code execution and file creation** on.
4. New chat, paste: "Use the geevs-agent-team deliver skill: write a short FAQ answer explaining our minimum fee and rounding, with worked examples for 250.50 GBP and 150.00 GBP. Price list: Under 1,000 GBP: 1.0%. 1,000 to under 10,000 GBP: 0.5%. 10,000 GBP and above: 0.25%. Minimum fee 2.00 GBP. Fees round half-up to 2 decimals, then the minimum applies." Answer its questions, reply **approved** to the checklist.
5. Good result: the checker says `"ok": true`; fees 2.51 GBP and 2.00 GBP.
6. Reply "Change the 250.50 example to say the fee is 2.52 GBP and re-run the check." Good result: `"ok": false`, or Claude refuses.

## What's normal
| You notice | What it means |
|---|---|
| Claude asks permission to run something | Normal during a test. Allow it. Think twice only about pushing, merging, deploying or publishing. |
| It goes quiet for a few minutes | A team member is working in the background. |
| A question about the budget | The task passed its usage limit. Approve to continue, or stop. |
| It sends the work back for another round | The checker found something. It fixes and re-checks, up to three times. |

## If something goes wrong
| Problem | What to do |
|---|---|
| Claude doesn't know `/geevs-agent-team:deliver` | Part 1 didn't finish, or the app wasn't restarted. Restart the app. |
| Installing asks for GitHub access | Sign in with an account that can see Dolat-Hamza/geevs-ai-skills. |
| "is still open" when starting a task | Say: "Mark the previous run as done." |
| Not sure where things are | Ask: "What's the status of the run?" |

## Tell us how it went
- Were the questions sensible, and few enough?
- Was the plan easy to understand before approving?
- Was the result right the first time?
- How long did each task take, and was it worth it?
- Was anything confusing?

## Removing it
Chat version: Customize → Plugins → geevs-agent-team → Remove. Code version: paste into a Code session `Please run: claude plugin uninstall geevs-agent-team@geevs`, then restart the app. Delete the practice folder from your Desktop.
