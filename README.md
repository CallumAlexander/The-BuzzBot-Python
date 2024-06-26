# The BuzzBot

[![wakatime](https://wakatime.com/badge/user/eb310a2d-fc37-4859-8755-b6b88930af57/project/018cdb8d-3c59-4706-8b4c-4fb2808b90c9.svg)](https://wakatime.com/badge/user/eb310a2d-fc37-4859-8755-b6b88930af57/project/018cdb8d-3c59-4706-8b4c-4fb2808b90c9)

`If the EUHC Cinematic Universe allowed Jack Mead, Ed Bury, and I to do the umpiring assignments for EUMHC together at the same time. Then times that by 10 million. That is The BuzzBot`

## A note to users and contributors

This software and accompanying documentation has been developed specifically for [Edinburgh University Men's Hockey Club](www.euhc.co.uk).
Much of the graphical interface and backend logic may not be applicable and/or relevant to other domains. Anyone is more than welcome to use and edit the software in this repository for their own purposes. We encourage you to explore, modify, and adapt the code to fit your needs.

For detailed information about using, copying, modifying, and distributing this software, please refer to the [LICENSE](./LICENSE) file in this repository.

## Abstract

Students don't like umpiring. In an ideal world, every player at a university hockey club would never have to umpire
a game during their time at the club. Alas, this is not the case. At Edinburgh University Men's Hockey Club, the club
policy
is that all umpires are players; the two are not mutually exclusive like they are at other clubs. When priority is given
to ensure all players are able to put playing first, a system for assigning umpires to fixtures can be modelled. Given a
uniform spread of umpires across all playing teams, assignments can be given to a team rather than an individual. The
system
presented, called The BuzzBot, successfully assigns 'covering teams' to fixtures based on set assumptions and
constraints.

## Constraints, Heuristics, and Assumptions

### Heuristic: **GreedyFair** - Uniform assignment based on Team Ranking and Umpiring Ability

The **GreedyFair** heuristic ensures that umpiring duties are distributed uniformly among teams based on their ranking and umpiring ability. The key assumption is that the higher-ranked teams with regard to their playing ability have better umpiring abilities. Thus, if team $t_1$ is ranked higher than team $t_2$, then the umpiring ability of $t_1$ is greater than the umpiring ability of $t_2$.

#### Team Selection Process

1. **Initialisation**:
  - Let $T$ be the set of all teams.
  - Let $A(t)$ be the number of current assignments for team $t$.

2. **Selection Criteria**:
  - At each selection step, choose the team $t$ that satisfies:
   $$t = \arg\min_{t' \in T} A(t')$$
    Among the teams with the minimum number of current assignments, select the highest-ranked team.

3. **Assignment**:
  - Assign the selected team $t$ to the current umpiring duty.
  - Increment the assignment count: $A(t) = A(t) + 1$.

#### Mathematical Representation

1. **Define**:
  - $R(t)$: Rank of team $t$ (lower value means higher rank).
  - $A(t)$: Number of assignments for team $t$.

2. **Selection Function**:
  - Let $T_{\min}$ be the set of teams with the minimum number of assignments:
   $$T_{\min} = \{ t \in T \mid A(t) = \min_{t' \in T} A(t') \}$$

  - Choose the team $t$ from $T_{\min}$ with the highest ranking:
   $$t = \arg\min_{t' \in T_{\min}} R(t')$$

3. **Update**:
  - Assign team $t$ to the current umpiring duty.
  - Update the number of assignments for team $t$:
   $$A(t) = A(t) + 1$$

By following this heuristic, the best umpiring team does not get assigned every match, ensuring a balanced distribution of umpiring duties across all teams.

### Constraint: Umpire Cannot Play and Umpire Simultaneously
An umpire $u$ cannot umpire and play at the same time.

$$
u \text{ umpires game } g \implies u \notin \text{players}(g)
$$

### Constraint: Fixture Overlap
An umpire cannot umpire a fixture if the fixture overlaps with their own playing fixture. For fixtures $A$ and $B$ in the list of fixtures $F$:

$$
\neg (A_{\text{start}} < B_{\text{end}} \land A_{\text{end}} > B_{\text{start}})
$$

### Constraint: Travel Time Between Fixtures
An umpire cannot umpire a fixture if the time between the umpiring fixture and the playing fixture is less than the total travel time between the two. Let $T_{AB}$ be the travel time between fixtures $A$ and $B$:

$$
A_{\text{end}} + T_{AB} \leq B_{\text{start}}
$$
$$
B_{\text{end}} + T_{BA} \leq A_{\text{start}}
$$

### Assumption: Symmetric Travel Time
The travel time from fixture $A$ to fixture $B$ is equal to the travel time from fixture $B$ to fixture $A$.

$$
T_{AB} = T_{BA}
$$

### Assumption: Mode of Travel
Umpires travel to and from games in cars.




## Prerequisites

Make sure you have the following installed on your system:

- Python (>=3.6)
- pip (Python package installer)
- Virtualenv (optional but recommended)

## Installation

### Clone the Repository

```bash
git clone https://github.com/CallumAlexander/The-BuzzBot-Python.git
cd The-BuzzBot-Python
```

### Install Dependencies

Install the required Python packages using pip:

```bash
pip install -r requirements.txt
```


## Running the Application

To start the Flask application, use the following command:

```bash
flask run
```

By default, the application will run on `http://127.0.0.1:5000/`. Navigate to there in your browser.

## To-do list of things to do
- [x] Prioritised covering selection for teams playing on the same day
- [x] Doesn't select the playing team as the covering team
- [x] Doesn't select teams that are playing in overlapping times
- [x] Handles requiring no umpires and requiring 2 umpires
- [x] Add location to fixtures
  - [x] Integrate travel time calculation and overlap checking using Google Maps API(?)
- [ ] Handle having a teams as an away team in a fixture
- [ ] Heuristic involving confidence metric to select the best team to umpire rather than a greedy heuristic
- [ ] Rewrite as a proper constraint search problem.
- [ ] Handle multiple team assignments for a single game (1s and 2s provide an umpire each for a match - only when 2
  umpires are required).