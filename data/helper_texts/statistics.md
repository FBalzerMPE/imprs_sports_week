Here, we provide some explanations as to how the teams were formed and the matches were scheduled. Also, you can find some overview plots in the end.

## Building the teams

When first coming up with the idea to group all of you into three different main teams that would send out players for each fo the sports, the question of how to compose these teams came up - how could we make sure that there'd be enough players available for each sport, in each of the teams? Given how ununiform the survey had been filled out (some of you only wanted to participate in a single sport, some wanted to participate in all of them, but many preferred weird combinations).\
We were thus faced with an optimization problem that I'm sure could be rigorously solved using fancy maths. We instead opted for an easier solution by defining an *equality index* $f_{\rm eq}$ assessing the approximate equality of the three teams, and tried to add players one by one. This index would be defined as $f_{\rm eq}=\sum_{i=1}^{11}\frac{\sigma_i}{\mu_i}$, where $\sigma_i$ and $\mu_i$ would be the standard deviation and mean number of players for sport $i$ amongst the three teams.\
We would calculate $f_{\rm eq}$ by simulating adding the player to each of the teams, and would then add them to the one where $f_{\rm eq}$ would be minimized. While this worked out alright, the balancing still left a few things to be desired. We then tried a few things to improve upon this; our scheme depends on the order that the participants are added, so it made sense to shuffle them in beforehand.\
The first approach for this involved hunting for the perfect shuffling seed, but then we figured it might just be easier to order the players by the amount of sports they did, as it would be easier to add players that did a low amount of sports later.\
This approach worked well, although we did a random adjustment in the sorting that somehow more or less perfectly balanced the teams (the dip in basketball for team 3 is due to someone that was added later).

## Some plots

The following plots provide an overview of some attributes of the more than 90 participants of the sports week.

Note that these plots contain updated values; Due to latecomers and drop-outs, the teams aren't as evenly distributed as initially (but it's still pretty alright).
