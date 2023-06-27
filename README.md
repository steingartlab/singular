# Singular

### Overture

At Club Steingart and CEEC we are so fortunate to have access to pretty much every piece of battery testing instrument there is, including at least five types of battery cyclers. However, loading, parsing, and analyzing data from such a variety of sources—each OEM seems to revel in creating their own proprietary format—can be a suboptimal experience.

To ameliorate this, we have this abstraction called `singular`. It achieves two things:

1. A single function to load *all* electrochemical cycling data
2. Standardized contents

# How to use

```
from main import load

id_ = 'dummy_id'

echem = load(id_=id_)
```

Just change `id_` to match your needs. No absolute path. No specifying file type. No parsing column names. No specific function for each type of cycler.

# Nitty-gritty

### Cyclers

At the time of writing, `singular` handles the following cyclers:

- `biologic`
- `ivium`
- `neware`
- `squidstat`

### Fields

It will return a `pandas dataframe` with the following columns

- ALWAYS
    - `time` (as index). It is either a) a *unix timestamp* or, b) time elapsed [s]. See subsection *Time after time ♬*  for more details
    - `voltage`
    - `current`
    - `cycle`
- IF INCLUDED IN RAW DATA
    - `capacity`
    - `dcapacity`

This is convenient as it makes rehashing code across different cyclers simpler. No more “**is it ‘Ewe/V’ or is it ‘Working Electrode (V)**’?”.

(Other fields like `dQ/dV` could easily be added but ppl seem to have their personal preference for calculating it)

### Other points

- It handles CC/CV/CCCV/OCP, *not* EIS
- `neware`: For `id_`, it can either be the *anyware* ID (e.g. 230158-2-6-562) or the experiment ID (field “info” on anyware’s inspect).

- `neware`: It automatically concatenates data from *anyware* with same experiment ID, but different anyware IDs ****a la**** Rob Mohr
- It assumes data from `biologic`, `squidstat`, and `ivium` resides on `labdaq` (a first class citizen on `drops`).

### Time after time ♬

> **Prologue**: *If you’re only running electrochemistry, i.e. nothing measuring anything else, you don’t need to consider this part*
> 

At some point in every grad student’s life, you will run something in tandem with electrochemistry. That is the Club Steingart™️ way. This can be anything from acoustics to pressure, temperature, or even crystal oscillation. These multi-source data streams must be temporally synced in post. This is not the place to discuss that deceptively tricky topic in detail, but we need to touch on it.

This writer's opinionated opinion on how to handle electrochemical data is to parse timestamps as [unix timestamps](https://www.unixtimestamp.com/) and set them as the pandas dataframe’s index. Anyware automatically handles this for neware data, but the other (stupid) formats only contain elapsed time by default.

On `squidstats`, it will first look for a column called `UTC Time (s)`. In case it is not there, it will set the time column as time elapsed. For both `biologic` and `ivium`, it will have the time column as time elapsed. For those, the absolute timestamps can be added after calling `singular.load(id_)`.


## The code


> 🌸 I will do my absolute best to maintain this with backwards compatibility in mind. However, I assume no responsibility for code suddenly breaking in case I make changes. As such, and if you think you’ll use this heavily, it may be a good idea to fork the pithy script.
