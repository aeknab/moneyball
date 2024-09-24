pie_chart_prompt_template = """
Hey {player_name}, let’s break down how your predictions stack up in the big picture.

You’re looking at a **donut chart** that shows the distribution of your predictions compared to actual Bundesliga results. The chart helps you see where you’re nailing it and where your predictions are drifting off course.

### Here’s the deal:
- **Wins**: You predict wins {win_percentage:.1f}% of the time, while the Bundesliga sees actual wins in {results_win_percentage:.1f}% of games.
- **Draws**: You predict draws {user_draw_percentage:.1f}% of the time, but draws occur {actual_draw_percentage:.1f}% of the time. That’s a significant gap!
- **Losses**: You predict losses {lose_percentage:.1f}% of the time, while Bundesliga matches end in away wins {results_lose_percentage:.1f}% of the time.

### What does this mean?
You're under-predicting draws by a solid margin. Bundesliga matches are ending in draws {actual_draw_percentage:.1f}% of the time, but you’re only predicting them {user_draw_percentage:.1f}% of the time. You’re also a bit off on away wins.

### Recommendations:
- **Tighten up your draw predictions**. It looks like you’re skipping too many. Get more comfortable with predicting draws when matches are tight.
- **Balance out win and loss predictions**. Try to mirror the actual distribution more closely, and remember: teams don’t win or lose all the time.
  
So, here's the plan: analyze past matchups and league trends to spot where you're misjudging. Focus especially on those draw scenarios that keep slipping through the cracks. The more you sync up with real results, the better your prediction game will be!

Now go make those predictions count!
"""