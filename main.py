from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.layout import Layout
from rich.text import Text
from rich.progress import Progress, BarColumn, TextColumn
from rich.table import Table
from rich import box
from rich.align import Align
from pyfiglet import Figlet
import time
import random
from animations import ANIMATION_SETS

class Tamagotchi:
    def __init__(self, name, pet_type="cat"):
        self.name = name
        self.hunger = 50
        self.happiness = 50
        self.health = 50
        self.energy = 100
        self.age = 0
        self.stage = "Baby"
        self.last_action = None
        self.animation_frame = 0
        self.pet_type = pet_type
        
        # Load animations from the animation sets
        if pet_type in ANIMATION_SETS:
            self.animations = ANIMATION_SETS[pet_type]
        else:
            # Default to cat if the specified type doesn't exist
            self.animations = ANIMATION_SETS["cat"]
    
    def feed(self):
        self.hunger = max(0, self.hunger - 15)
        self.happiness = min(100, self.happiness + 5)
        self.energy = max(0, self.energy - 5)
        self.last_action = "eating"
        
    def play(self):
        self.happiness = min(100, self.happiness + 15)
        self.hunger = min(100, self.hunger + 10)
        self.energy = max(0, self.energy - 20)
        self.last_action = "playing"
        
    def heal(self):
        self.health = min(100, self.health + 15)
        self.happiness = max(0, self.happiness - 5)
        self.energy = max(0, self.energy - 10)
        self.last_action = "healing"
        
    def sleep(self):
        self.energy = min(100, self.energy + 40)
        self.health = min(100, self.health + 5)
        self.happiness = max(0, self.happiness - 5)
        self.last_action = "sleeping"
    
    def get_animation_frame(self):
        # Determine animation based on pet state
        if self.health < 30:
            animation_type = "sick"
        elif self.last_action == "sleeping":
            animation_type = "sleeping"
        elif self.happiness > 80:
            animation_type = "happy"
        elif self.last_action:
            animation_type = self.last_action
        else:
            animation_type = "idle"
            
        frames = self.animations.get(animation_type, self.animations["idle"])
        return frames[self.animation_frame % len(frames)]
    
    def tick(self):
        self.hunger = min(100, self.hunger + 2)
        self.happiness = max(0, self.happiness - 1)
        self.health = max(0, self.health - (2 if self.hunger > 80 else 0))
        self.energy = max(0, self.energy - 1)
        self.animation_frame += 1
        
        # Age increases every 10 ticks
        if self.animation_frame % 10 == 0:
            self.age += 1
            
        # Evolution stages
        if self.age >= 30:
            self.stage = "Adult"
        elif self.age >= 15:
            self.stage = "Teen"
        else:
            self.stage = "Baby"
            
        # Random events (5% chance)
        if random.random() < 0.05:
            event = random.choice(["hunger", "happiness", "health", "energy"])
            if event == "hunger":
                self.hunger = min(100, self.hunger + 10)
            elif event == "happiness":
                self.happiness = max(0, self.happiness - 10)
            elif event == "health":
                self.health = max(0, self.health - 5)
            elif event == "energy":
                self.energy = max(0, self.energy - 15)

    def is_alive(self):
        return self.health > 0 and self.hunger < 100
        
    def status(self):
        if self.health < 30:
            return "Sick"
        elif self.hunger > 70:
            return "Hungry"
        elif self.happiness < 30:
            return "Sad"
        elif self.energy < 30:
            return "Tired"
        elif self.happiness > 80:
            return "Joyful"
        else:
            return "Normal"


def create_pet_display(pet):
    # Create layout
    layout = Layout()
    layout.split_column(
        Layout(name="header"),
        Layout(name="body"),
        Layout(name="footer")
    )
    
    # Header
    f = Figlet(font='small')
    header_text = f.renderText(f"Tamagotchi - {pet.name}")
    layout["header"].update(Align.center(Text(header_text, style="bold cyan")))
    
    # Body
    body_layout = Layout()
    layout["body"].update(body_layout)
    body_layout.split_row(
        Layout(name="stats"),
        Layout(name="pet")
    )
    
    # Stats panel
    table = Table(box=box.ROUNDED, expand=True)
    
    table.add_column("Status", style="cyan")
    table.add_column("Value", style="green")
    
    # Progress bars for stats (static bar)
    def make_bar(value, color):
        bar_length = 20
        filled = int(bar_length * value / 100)
        empty = bar_length - filled
        bar = f"[{color}]{'█' * filled}{' ' * empty}[/] {value:3d}%"
        return bar
    
    hunger_color = "yellow" if pet.hunger < 70 else "red"
    health_color = "green" if pet.health > 30 else "red"
    happiness_color = "magenta" if pet.happiness > 30 else "red"
    energy_color = "blue" if pet.energy > 30 else "red"
    
    table.add_row("Hunger", make_bar(pet.hunger, hunger_color))
    table.add_row("Health", make_bar(pet.health, health_color))
    table.add_row("Happiness", make_bar(pet.happiness, happiness_color))
    table.add_row("Energy", make_bar(pet.energy, energy_color))
    
    table.add_section()
    table.add_row("Status", f"[bold]{pet.status()}[/bold]")
    table.add_row("Age", f"[bold]{pet.age}[/bold] days")
    table.add_row("Stage", f"[bold]{pet.stage}[/bold]")
    table.add_row("Pet Type", f"[bold]{pet.pet_type.capitalize()}[/bold]")
    
    body_layout["stats"].update(Panel(table, title="Stats", border_style="green"))
    
    # Pet panel - animation with more visual appeal
    pet_animation = pet.get_animation_frame()
    # Clean up and center the ASCII art
    pet_lines = [line.rstrip() for line in pet_animation.strip('\n').split('\n')]
    max_width = max(len(line) for line in pet_lines)
    # Pad each line to the same width
    padded_lines = [line.center(max_width) for line in pet_lines]
    # Add vertical padding
    vertical_pad = 2
    padded_lines = ([" " * max_width] * vertical_pad) + padded_lines + ([" " * max_width] * vertical_pad)
    pet_art_block = "\n".join(padded_lines)

    # Add colors to the pet animation based on status
    if pet.health < 30:
        pet_color = "red"
    elif pet.happiness > 80:
        pet_color = "bright_magenta"
    elif pet.last_action == "eating":
        pet_color = "yellow"
    elif pet.last_action == "playing":
        pet_color = "bright_green"
    elif pet.last_action == "healing":
        pet_color = "bright_blue"
    elif pet.last_action == "sleeping":
        pet_color = "bright_white"
    else:
        pet_color = "cyan"
        
    # Add sparkles and visual elements based on pet stage
    if pet.stage == "Baby":
        decoration = "★ "
    elif pet.stage == "Teen":
        decoration = "⚡ "
    else:  # Adult
        decoration = "👑 "
    
    # Create the pet display with decorations
    pet_display_str = f"\n{decoration}{pet.stage} {decoration}\n\n"
    pet_display_str += f"[{pet_color}]{pet_art_block}[/]\n\n"
    
    # Add speech bubble with message
    if pet.last_action == "eating":
        message = "Yum yum, delicious!"
    elif pet.last_action == "playing":
        message = "Wheee! This is fun!"
    elif pet.last_action == "healing":
        message = "I feel better now!"
    elif pet.last_action == "sleeping":
        message = "Zzz... Zzz..."
    else:
        message = random.choice([
            "I love you!",
            "Let's play!",
            "I'm bored...",
            "What shall we do today?",
            "Hi there!",
            f"I'm a {pet.stage.lower()} now!",
            "Feed me!",
            "Care for me!",
        ])
    
    # Create a speech bubble
    speech_width = len(message) + 4
    pet_display_str += f"  ╭{'─' * speech_width}╮\n"
    pet_display_str += f"  │  {message}  │\n"
    pet_display_str += f"  ╰{'─' * speech_width}╯\n"
    
    pet_display = Text.from_markup(pet_display_str, justify="center")
    
    body_layout["pet"].update(Panel(
        Align.center(pet_display, vertical="middle"),
        title=f"[{pet_color}]{pet.name}[/] - {pet.status()}",
        border_style="magenta",
        box=box.DOUBLE
    ))
    
    # Footer
    footer_text = "Commands: [bold cyan]F[/bold cyan]eed | [bold cyan]P[/bold cyan]lay | [bold cyan]H[/bold cyan]eal | [bold cyan]S[/bold cyan]leep | [bold cyan]C[/bold cyan]hange Pet | [bold cyan]Q[/bold cyan]uit"
    layout["footer"].update(Panel(Align.center(footer_text), border_style="blue"))
    
    return layout

def show_title_screen(console):
    console.clear()
    f = Figlet(font='slant')
    title = f.renderText("Tamagotchi")
    subtitle = "A Virtual Pet Game"
    
    panel = Panel(
        f"[bold cyan]{title}[/bold cyan]\n\n[yellow]{subtitle}[/yellow]\n\n[green]Press Enter to start...[/green]",
        box=box.DOUBLE,
        border_style="cyan",
        width=80
    )
    console.print("\n" * 2)
    console.print(Align.center(panel))
    input()

def show_game_over(console, pet):
    console.clear()
    f = Figlet(font='slant')
    title = f.renderText("Game Over")
    
    cause = "unknown"
    if pet.health <= 0:
        cause = "got too sick"
    elif pet.hunger >= 100:
        cause = "got too hungry"
    
    panel = Panel(
        f"[bold red]{title}[/bold red]\n\n[yellow]{pet.name} {cause} and has passed away.[/yellow]\n\nAge: {pet.age} days\nFinal Stage: {pet.stage}\n\n[green]Thank you for playing![/green]",
        box=box.DOUBLE,
        border_style="red",
        width=80
    )
    console.print("\n" * 2)
    console.print(Align.center(panel))

def show_action_animation(console, pet, action_name, frames=5):
    """Show a brief animation when an action is performed."""
    for _ in range(frames):
        console.clear()
        pet.animation_frame += 1
        console.print(create_pet_display(pet))
        time.sleep(0.2)
        
def select_pet_type(console):
    """Let the user select a pet type."""
    console.clear()
    f = Figlet(font='small')
    title_text = f.renderText("Choose Your Pet")
    
    panel = Panel(
        f"[bold cyan]{title_text}[/bold cyan]\n\n"
        f"[yellow]Select your pet type:[/yellow]\n\n"
        f"[green]1. Cat[/green] - A cute feline friend\n"
        f"[green]2. Bunny[/green] - A fluffy bunny companion\n"
        f"[green]3. Robot[/green] - A mechanical buddy\n",
        box=box.DOUBLE,
        border_style="cyan",
        width=80
    )
    
    console.print("\n" * 2)
    console.print(Align.center(panel))
    
    choice = Prompt.ask(
        "[bold cyan]Enter your choice[/bold cyan]",
        choices=["1", "2", "3"],
        default="1"
    )
    
    if choice == "1":
        return "cat"
    elif choice == "2":
        return "bunny"
    else:
        return "robot"

def main():
    console = Console()
    
    # Make terminal screen suitable for animations
    console.set_alt_screen(True)
    
    try:
        show_title_screen(console)
        
        # Select pet type
        pet_type = select_pet_type(console)
        
        console.clear()
        name = Prompt.ask("[bold cyan]What is your Tamagotchi's name?[/bold cyan]")
        pet = Tamagotchi(name, pet_type)
        
        # Show idle animation before starting game
        for _ in range(3):
            console.clear()
            pet.animation_frame += 1
            console.print(create_pet_display(pet))
            time.sleep(0.3)
            
        while pet.is_alive():
            # Clear the screen and show the current state
            console.clear()
            console.print(create_pet_display(pet))
            
            # Show command prompt
            action = Prompt.ask(
                "\n[bold cyan]Choose your action[/bold cyan]",
                choices=["f", "p", "h", "s", "c", "q"],
                show_default=False
            ).lower()
            
            if action == 'f':
                pet.feed()
                show_action_animation(console, pet, "eating")
            elif action == 'p':
                pet.play()
                show_action_animation(console, pet, "playing")
            elif action == 'h':
                pet.heal()
                show_action_animation(console, pet, "healing")
            elif action == 's':
                pet.sleep()
                show_action_animation(console, pet, "sleeping")
            elif action == 'c':
                # Change pet type
                new_type = select_pet_type(console)
                pet.pet_type = new_type
                pet.animations = ANIMATION_SETS[new_type]
                show_action_animation(console, pet, "idle")
            elif action == 'q':
                break
            
            pet.tick()
            
            # Show idle animation between actions
            for _ in range(2):
                console.clear()
                pet.animation_frame += 1
                console.print(create_pet_display(pet))
                time.sleep(0.3)
        
        show_game_over(console, pet)
    finally:
        # Always restore the normal screen
        console.set_alt_screen(False)

if __name__ == "__main__":
    main()
