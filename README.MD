My Halite 2 Bot

Started around halfway into the season and placed 22nd on the final leaderboard! My final submission was Bot60.py

I was gonna do a writeup about my bot, but totally forgot to. I tried to look at my code and think it's best to not do one anymore.

This was the first time I programmed any sort of bot for a game and it was definitely super fun. Looking forward to the next season!

Some observations/takeaways for the future:

1. Improvement in the lower ranks mainly came from copying the general overarching strategy that should be followed as well as implementing correct mechanics/basic behavior. Copying people op, don't theorycraft until higher ranks.
2. Improvement in the higher ranks mainly came from spending a lot of time to finetune random constants/micro behaviors that could make small differences. The things causing improvements sometimes felt very unintuitive/random.
3. Lots of non-transitive performance in the higher ranks (rank 6 usually beats rank 7 who usually beats rank 8, but rank 8 usually beats rank 6 etc.). Probably related to point 2. Quite hard to have "pareto-efficient" improvement in bot (adding some behavior to help against player X often slightly hurts performance against player Y), which is also why improvement in higher ranking was hard to strategize/reason about and felt more like yolo trial-and-error.
4. Using python probably wasn't a good choice since speed of execution mattered a lot. I couldn't implement certain behaviors due to high time cost. Also had to constantly worry about timing out and set multiple safety points to prevent that. Using a compiled language would've completely prevented that.
5. Don't worry too much about having structured code since it's hard to know how the code should be structured at first. Keep stuff simple and modular. Messy code is fine since you'll be looking at the code weekly too.
