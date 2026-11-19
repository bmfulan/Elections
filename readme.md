This project concerns presidential elections in the United States from 1980 to 2024.  The main focus will be on the margin of the two-party vote share in each state. For example, suppose that in a given year the Democratic candidate receives 55% of the two-party vote (the combined vote for the Democratic and Republican candidates) in State A and 40% in State B. Then the "Democratic Raw Margin" in State A is 55 - 45 = 10, and in State B it is 40 - 60 = -20.

A state's vote margin can be thought of as consisting of two components: the national vote margin and the state's deviation from the national margin. That second component is useful for analyzing how states shift relative to each other from election to election and how these shifts contribute to the Electoral College results. We define a state's "Democratic Adjusted Margin" by subtracting the national Democratic margin of the two-party vote share from the Democratic Raw Margin of that state.

To illustrate, this chart shows both the Democratic Raw Margin and the Democratic Adjusted Margin for a single state, Wisconsin, in each of the elections from 1980 to 2024. (Observations)

This chart shows the Democratic Adjusted Margin for every state (plus Washington DC) for each of the elections from 1980 to 2024. Note that values above zero mean that the Democratic candidate performed better in that state than in the nation as a whole, whereas values below zero indicate the same for the Republican candidate. (Observations)

(Show/discuss states that flipped from year to year?) 

(Are states that swing in one direction more likely to swing the same way or the opposite way in the following election? 3x3 grid of autocorrelation by year. Conclusion: r ~= 0 overall, generally r < 0 in elections with an incumbent and r > 0 with no incumbent)

One question this data can help us answer: if a state swings in one direction from one election to the next, in the following election is it more likely to swing in the same direction, the opposite direction, or is there no clear pattern? By looking at the Democratic Adjusted Margin, we can factor out swings in the national popular vote and focus on how states swing relative to each other.

This chart shows...

Next time: fill out analysis.py, plots.py, main.py