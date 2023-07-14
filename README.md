# Singular

### Overture

At Club Steingart and CEEC we are so fortunate to have access to pretty much every piece of battery testing equipment there is, including at least five types of cyclers. However, loading, parsing, and analyzing data from such a variety of sources—each OEM seems to revel in creating their own proprietary format—can be a suboptimal experience.

To ameliorate this, we have this abstraction called `singular`. It achieves two things:

1. A single function to load *all* electrochemical cycling data
2. Standardized contents

# How to use

Create a `config.json` with variable `base_directory` containing the absolute path to the root folder where all your data exists, e.g. `"base_directory": "/Users/cleese/electrochem"`. It does not matter whether the data sits in a subdirectory—the code will search recursively through all subdirectories.

```
from singular.implement import load

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

- _Always_
    - `time` (as index). It is either a) a *unix timestamp* or, b) time elapsed [s]. See subsection *Time after time ♬*  for more details
    - `voltage`
    - `current`
    - `cycle`
- _If included in raw data_
    - `capacity`
    - `dcapacity`

This is convenient as it makes rehashing code across different cyclers simpler. No more “**is it ‘Ewe/V’ or is it ‘Working Electrode (V)**’?”.

(Other fields like `dQ/dV` could easily be added but ppl seem to have their personal preference for calculating it)

### Other points  

- It handles CC/CV/CCCV/OCP, *not* EIS
- `neware`: For `id_`, it can either be the *anyware* ID (e.g. 230158-2-6-562) or the experiment ID (field “info” on anyware’s inspect).

- `neware`: It automatically concatenates data from *anyware* with same experiment ID, but different anyware IDs _a la_ Rob Mohr
- It assumes data from `biologic`, `squidstat`, and `ivium` resides on `labdaq` (a first class citizen on `drops`).

### Time after time ♬

> **Prologue**: *If you’re only running electrochemistry, i.e. nothing measuring anything else, you don’t need to consider this part*
> 

At some point in every grad student’s life, you will run something in tandem with electrochemistry. That is the Club Steingart™️ way. This can be anything from simple pressure and temperature logs to acoustics, calorimetry, or crystal oscillation. These multi-source data streams must be temporally synced in post. This is not the place to discuss that deceptively tricky topic in detail, but we need to touch on it.

This writer's opinionated opinion on how to handle electrochemical data is to parse timestamps as [unix timestamps](https://www.unixtimestamp.com/) and set them as the pandas dataframe’s index.

- Anyware automatically handles this for neware data, but the other (~stupid~) formats only contain elapsed time by default.

- On `squidstats`, it will first look for a column called `UTC Time (s)`. In case it is not there, it will set the time column as time elapsed

- For both `biologic` and `ivium`, it will have the time column as time elapsed. For those, the absolute timestamps can be added after calling `singular.load(id_)`.

## Adding a new cycler

1. `singular.py`

    Create a subclass of `Cycler`

2. `cyclers.py`

    Create a class initializer


## TODOs

As of 2023-06-30:

[ ] Current version relies on each cycler having different file endings. Will fix later if I add a cycler that breaks this pattern, but si fractum non sit, noli id reficere.

[ ] Get rid of `galvani` dependency


> 🌸 I will do my absolute best to maintain this with backwards compatibility in mind. However, I assume no responsibility for code suddenly breaking in case I make changes. As such, and if you think you’ll use this heavily, it may be a good idea to fork the pithy script.
