
The plots below provide an overview of some attributes of the more than ~~90~~ 115 participants of the 2024 Sports Week.

### Building the teams (for the first Sports Week)

When first coming up with the idea to group all players into three or more different main teams that would send out players for each fo the sports, the question of how to compose these teams came up - how do we make sure that there'd be enough players available for each sport in each of the teams?
Since the surveys had been filled out quite non-uniformly (some of you only wanted to participate in a single sport, some wanted to participate in all of them, but many preferred weird combinations), we were faced with an optimization problem.\
I'm sure this could be rigorously solved using fancy maths, but we instead opted for an easier solution: We start by defining an *equality index* $f_{\rm eq}$ assessing the approximate equality of the (incomplete) teams, and try to add players one by one. This index is defined as $f_{\rm eq}=\sum_{i=1}^{11}\frac{\sigma_i}{\mu_i}$, where $\sigma_i$ and $\mu_i$ is the standard deviation and mean number of players for sport $i$ amongst the teams.\
We calculate $f_{\rm eq}$ by looking how it changes when adding the player to any of the teams. Then we add them to the one where $f_{\rm eq}$ is minimized.

While this worked out alright overall for the first Sports Week, the balancing still left a few things to be desired. We therefore tried a few things to improve upon this; our scheme depends on the order that the participants are added, so it made sense to shuffle them in beforehand.\
The first approach for this involved hunting for the perfect shuffling seed, but then we figured it might just be easier to order the players by the amount of sports they did, as adding players that do a low amount of sports later is usually much more convenient.

This approach finally worked well, although we did a random adjustment in the sorting that somehow more or less perfectly balanced the teams (if you see any weird dips in the distribution now that might be because of rescheduled players and matches - by the end of this week, there were more than 150 movements of players between subteams due to drop-outs and jump-ins).
