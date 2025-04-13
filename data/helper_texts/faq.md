At the time of writing these questions, they luckily haven't been frequently asked, but let's hope they help to shed some light on things that might not be clear.

### Why all this hassle with the big teams and subteams? How does the scoring system work?

We have opted for this way of organizing the sports week as it offers advantages for planning the events, and it builds an overarching goal and structure for the whole week. You can look at the *Team Creation* tab for more information on how they were built from the survey results.\
For each sport, every subteam receives points for winning a match. These scores are mapped to a scale of 0 to 100 each, and multiplied by a weight factor that takes the amount of players into account which participate in the given sport. This ensures that each player in each sport will roughly have the same impact on the overall score in the end, and every contribution counts.

### Can I reschedule one of my ping pong matches?

Since ping pong is going to take place during the whole week and some of the slots are somewhat late, we allow you to easily reschedule a match, even to times not specified in our schedule - as long as your opponent agrees to it and the table you're opting for is available, you're free to find your own time.\
If you want to play during some of the main times, please first look at the general schedule and find a time and table that is not taken.\
After you've settled for a new time and place, please send Zsofi or Fabi an email (preferably with your opponent in cc), or a signal message.

### I have signed up for way more sports than I am now scheduled. Why?

To ensure a good flow during the events, we set up the schedules in ways to avoid overlaps for players, if you e.g. signed up for Basketball and Volleyball (which both take place on Monday), you will be scheduled as reserve for at least one of them. For all events except for Ping Pong, Foosball, Spikeball, and Tennis, that means that you may substitute in in whichever subteam you choose.\
This way, you are more flexible, and you won't encounter stressful double-bookings.

### I cannot make it on one of the days, can I still attend on the others?

Sure, just ensure you've notified us about any matches that you need to drop out of.

### Why and how did you generate the randomized names and avatars?

The nicknames (consisting of adjective + animal name each) are there such that we are able to display all information in an anonymous way.\
To generate them, simply used two publicly available lists, one of [adjectives]("https://gist.github.com/hugsy/8910dc78d208e40de42deb29e62df913") and one of [animal names](https://gist.github.com/EyeOfMidas/311e77b8b8c2f334fc8bdaf652c1f47f#file-animal-names-csv) (which we trimmed to only include single-word animals).\
From those, we generated randomized combinations to get the nicknames.\
A few days after this system was in place (during the preparations for the first sports week in 2024), Fabi had a conversation with a friend (shoutouts to Colin) who has access to ChatGPT-4 and thus Dall-E-3, and one thing led to the other.\
We access the AI's image generation via its API, downloading the pictures directly in the lowest resolution possible (1024x1024 px²).\
For this website, we then scaled those down (200x200 px²) to improve loading times, but let Fabi know if you want any higher-resolution originals.\
The exact prompt used was ```"Create an avatar showing a '{adj + animal}' (the animal) with a white background."```, although we redid a few ones. If you want to check out the code for yourself, see the `openai_image_download.py` script in the [github repo](https://github.com/FBalzerMPE/imprs_sports_week) of this page. There you can also find further details, f.e. we used the 'vivid' style of Dall-E-3.\
We are aware that by now even more impressive image generation models are online, but we've decided to stick with the original one to make the generation of the new avatars consistent with the one from previous years, so people can keep their old ones without sticking out. If you however would like your avatar to be redone, let Fabi know.
