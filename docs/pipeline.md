1. # Stage 1: Hybrid Onboarding (The Extractor Agent)
The Action: The user logs in and is greeted by the Guided Onboarding Wizard.
The Flow:
If they have documents (SSM, pitch deck), they drag and drop them. The Extractor Agent pulls the data.
If they don't have documents, the UI dynamically asks the 5-6 simple questions you proposed (Revenue range, operation time, sector).
The Result: The system generates the unified Company Profile, regardless of how they inputted the data.

# Stage 2: Instant Agentic Matching (The Evaluator Agent)
The Action: The system instantly cross-references the Company Profile against your pre-indexed Grant Database.
The Result: The user is taken to the Grant Dashboard. Every grant displays an Explainable Match Score and a Readiness Level (e.g., "75% Ready for MDEC Digital Grant").

# Stage 3: The Fork in the Road (Ready vs. Unready)
The user clicks on a specific grant. The UI branches based on their Readiness Level:

## Track A: The "Unready" SME (The Coach)
Trigger: Readiness score is below 80% (Missing critical items).
The UI: Displays the Grant Readiness Checklist (What you have vs. What you need).
The AI Action (Missing-Document Coach): For every missing item (e.g., "Audited Financial Statements"), the AI provides a simple explainer: "What this is: An official record of your finances approved by an accountant. Why you need it: Government grants require proof of financial stability. How to get it: Hire a certified company secretary or auditor."
The Outcome: The SME has a clear, actionable roadmap to become eligible.

## Track B: The "Ready" SME (The Drafter)
Trigger: Readiness score is high; core eligibility is met.
The UI: Moves straight to the Grant Application Checklist.
The AI Action (The Drafter Agent): As you brilliantly outlined, items are split into "Hard Docs" (requires manual upload) and "Soft Docs" (Pitch Decks, Proposals). The user clicks "Generate" on the soft docs. The Drafter Agent uses the GLM API to write the formal proposals based on the user's profile.
The Outcome: The user clicks "Download Submission Package", yielding a clean ZIP file containing their hard docs and the AI-generated proposals, ready for manual submission.

# Why This Pipeline Wins
1. Handles Ambiguity Flawlessly: The "Missing-Document Coach" directly satisfies the rubric's requirement to handle missing data and ambiguity in complex procedures.
2. High Utility: Even if an SME doesn't apply for a grant today, the Readiness Score and roadmap provide massive immediate value.
3. Safe & Demoable: By dropping the live scraper, you guarantee a snappy, impressive live demonstration. You can seamlessly show the "Unready" track for one grant, and the "Ready" track for another.

# Workflow:
1. User Account Generating
The user logs in/registers a user account.

2. Company Profile Setting
The user sets up a company profile, uploads essential company docs (e.g. SSM certs, financial statements …) assisted by a checklist of questions (e.g. target revenue, nationality…). An AI agent (Extractor agent) will extract the information and generate a formatted company profile (that will be exhibited in the “Company Profile” tab).

3. Grant Scaping
The user launches a scrapper (Scout agent) that scraps through the Internet to search for all grants information (both eligible and not eligible). Then the grants are stored and displayed in the “Grant” tab. Outdated grants will be removed from the database after each scrap. After scrapping the user needs to force the Scout agent to stop scrapping (maximum scrapping limit is 8 hours). An (Evaluator agent) will then check the company profile and each grant found to check how the company is eligible for the grant, then generate a tag (status) beside each grant in the grant list.

4. Grant Application
The user reviews the “Grant” tab, looks for an interested grant, clicks into it. The UI will lead the user to another endpoint. In that endpoint, it will display a checklist of documents needed to be submitted in order to apply for the grant with a completion mark beside each checklist item that indicates whether a required document is present or absent. For items that AI can’t generate (like financial statements), there’re just a completion mark and an upload button attached to the item; for items that AI can generate (like pitch deck and proposal), there’s an additional button called generate, that can call the (Drafter agent) to generate the document. After all, the user can download all documents needed to apply that grant into a zip file, the downloaded zip file is ready to be submitted to the official portal manually by the user himself (because AI can't pass the “Human Verification” barrier at the official portals.)