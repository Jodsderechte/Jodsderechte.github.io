Mythistone displays the most advantageous information players can use to guarantee their success in the video game **World of Warcraft**, specifically in **Mythic+**.

---

## What is a video game

Think of a video game like an interactive TV show combined with a board game:  
- **Interactive story and challenge.** Players control characters on screen and make decisions in real time.  
- **Skills & teamwork.** Success often depends on quick thinking, strategy, and working with others.  
- **Global competition.** Millions of people play online and compare their performance.
---

## What is World of Warcraft?

- **Genre & Scale:** WoW is a massive online role-playing game (MMORPG) where hundreds of thousands of players connect at once.  
- **Character Development:** Each player creates a _character_ (avatar) that levels up by gaining experience, learning new abilities, and collecting better equipment.  
- **Collaboration & Competition:** Players team up to tackle tough challenges or compete against one another, not unlike cross-functional teams collaborating on a complex project.

---

## What is Mythic+

- **Dungeon Challenges:** “Dungeons” are instanced, multi-stage challenges. Think of them as time-boxed hackathons or project sprints with escalating difficulty.  
- **Scaling Difficulty:** Mythic+ applies a difficulty “multiplier” to each dungeon, so teams must coordinate faster and optimize every skill to meet strict time limits.  
- **Leaderboards & Performance Metrics:** Runs are timed and scored. Higher scores reflect better teamwork, strategy, and individual performance.

---

## What is Mythistone

- **Purpose:** Mythistone is a web-based analytics platform for WoW players. It collects performance data from thousands of Mythic+ runs and presents it in clear, actionable formats.  
- **Key Features:**
    - **Build Recommendations:** Which abilities (“talents”) and skill allocations deliver the best results for a given role? Similar to recommending a candidate’s optimal skill set for a job.  
    - **Gear Optimization:** Which equipment pieces yield the best performance gains? Comparable to advising on certifications or tools that boost on-the-job productivity.  
    - **Talent Profiles & Reports:** Visual summaries of what top performers are choosing. Like benchmark reports showing industry best practices.

---

## How It Was Built

1. **Data Source:** Blizzard provides an official API exposing Mythic+ leaderboards and character profiles (equipment, talents, performance).  
2. **Collection Pipeline:**
     - A Python script (“runner”) runs continuously on a Windows server, polling Blizzard’s API for updated leaderboard and character data.  
     - Retrieved data is inserted into a MySQL database hosted on an Ubuntu server.  
3. **Site Generation:**
     - GitHub Actions workflows trigger Python jobs that pull fresh data from MySQL.  
     - Using Jinja templates, these jobs render fully static HTML pages (builds, gear guides, leaderboards).  
4. **Deployment:**
     - Static pages are pushed to a GitHub Pages branch, instantly publishing the updated site with zero-downtime.  
