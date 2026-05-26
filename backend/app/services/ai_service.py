import os
from typing import Any

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


SUPPORTED_STYLES = {
    "dramatic commentator",
    "technical race engineer",
    "documentary narrator",
    "social media caption",
    "beginner-friendly explanation",
}


def normalize_style(style: str) -> str:
    clean_style = style.strip().lower()

    if clean_style in SUPPORTED_STYLES:
        return clean_style

    return "dramatic commentator"


def build_fallback_commentary(
    rider: str,
    race: str,
    scenario: str,
    style: str,
    duration_seconds: int,
) -> str:
    if style == "technical race engineer":
        return (
            f"Technical analysis for {rider} at {race}: {scenario}. "
            f"The key factors here are track position, tire management, braking stability, "
            f"and consistency over the race distance. From an engineering perspective, this kind "
            f"of performance depends on maintaining corner entry confidence, protecting rear tire grip, "
            f"and choosing overtaking moments without overheating the tire. "
            f"For a {duration_seconds}-second segment, the story is clear: controlled aggression, "
            f"calculated risk, and strong execution."
        )

    if style == "documentary narrator":
        return (
            f"In the story of {race}, {rider} becomes the focus of a defining racing moment. "
            f"{scenario}. It is the kind of performance that shows how MotoGP is not only about raw speed, "
            f"but also timing, patience, race intelligence, and pressure management. "
            f"Every braking zone, every corner exit, and every decision contributes to the final result."
        )

    if style == "social media caption":
        return (
            f"{rider} at {race}: {scenario}. "
            f"Pure MotoGP intensity. Late braking, big commitment, and no room for hesitation. "
            f"This is why racing hits different. 🏁🔥"
        )

    if style == "beginner-friendly explanation":
        return (
            f"Here is what happened with {rider} at {race}: {scenario}. "
            f"In simple terms, this means the rider had to manage speed, risk, tire grip, and overtakes. "
            f"In MotoGP, a strong result is not only about being fast for one lap. "
            f"The rider must stay consistent, avoid mistakes, and make smart moves at the right time."
        )

    return (
        f"And here comes {rider} at {race}! {scenario}. "
        f"This is MotoGP pressure at full speed — the bike moving on the limit, the rider searching "
        f"for every meter under braking, every advantage on corner exit, and every chance to attack. "
        f"The crowd can feel it, the pit wall can feel it, and the race is alive. "
        f"{rider} is not just riding; this is commitment, courage, and racecraft under pressure."
    )


def generate_commentary(request: Any) -> dict:
    rider = request.rider.strip()
    race = request.race.strip()
    scenario = request.scenario.strip()
    style = normalize_style(request.style)
    duration_seconds = request.duration_seconds

    if not rider:
        rider = "the rider"

    if not race:
        race = "the race"

    if not scenario:
        scenario = "delivered a strong racing performance under pressure"

    api_key = os.getenv("OPENAI_API_KEY")

    if api_key and OpenAI is not None:
        client = OpenAI(api_key=api_key)

        prompt = f"""
Generate MotoGP-style racing commentary.

Rider: {rider}
Race/Event: {race}
Scenario: {scenario}
Style: {style}
Approximate duration: {duration_seconds} seconds

Rules:
- Make it exciting and realistic.
- Use motorcycle racing language.
- Do not invent official statistics.
- If exact details are missing, keep the commentary general.
- Match the requested style.
- Keep it suitable for a portfolio demo.
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are RaceMind AI, a MotoGP commentary generator. "
                        "You create realistic motorcycle racing commentary without inventing official statistics."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0.8,
        )

        commentary = response.choices[0].message.content

        return {
            "commentary": commentary,
            "style": style,
            "rider": rider,
            "race": race,
            "used_openai": True,
        }

    fallback = build_fallback_commentary(
        rider=rider,
        race=race,
        scenario=scenario,
        style=style,
        duration_seconds=duration_seconds,
    )

    return {
        "commentary": fallback,
        "style": style,
        "rider": rider,
        "race": race,
        "used_openai": False,
    }