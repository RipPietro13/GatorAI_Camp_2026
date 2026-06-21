# Day 2: Sprites & Game Logic

Today we'll learn about Sprites and Game Logic by modifying the player!

## Step 1: Add a Custom Character
Open `settings.py` and find `@STUDENT-EDIT-Day2-1`.
Add a custom sprite image name to the character list. This lets you pick a different character for the NPC!

## Step 2: Change Player Speed
Open `settings.py` and find `@STUDENT-EDIT-Day2-2`.
Change the `PLAYER_SPEED` variable to make the player move faster or slower.

## Step 3: Modify Starting Direction
Open `player.py` and find `@STUDENT-EDIT-Day2-3`.
Change the player's starting direction from `"down_idle"` to `"left_idle"`, `"right_idle"`, or `"up_idle"`.

## Step 4: Add a Boundary Check
Open `player.py` and find `@STUDENT-EDIT-Day2-4`.
Add an `if` statement to prevent the player from leaving the screen vertically. For example:
```python
if self.pos.y < 0:
    self.pos.y = 0
```

## Step 5: WASD Movement Control
Open `player.py` and find `@STUDENT-EDIT-Day2-5`.
We want to allow the player to move using WASD instead of just the arrow keys. Use the logical `or` operator in Python to check both!
```python
if keys[pygame.K_UP] or keys[pygame.K_w]:
    self.direction.y = -1
    self.status = "up"
```
Do this for all four directions!
