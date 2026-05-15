import os
import logging
import requests

HUGGINGFACE_API_KEY_ENV_VAR = "HUGGINGFACE_API_KEY"
HUGGINGFACE_MODEL_ENV_VAR = "HUGGINGFACE_MODEL"

logger = logging.getLogger(__name__)

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    import openai
except ImportError:
    openai = None


def _build_prompt(profile: dict, scores: dict, salary: dict) -> str:
    prompt = [
        "Vyhodnoť následující profil kandidáta a napiš stručné vysvětlení:",
        "\n---\n",
        f"Shrnutí: {profile.get('summary', 'N/A')}",
        f"\nDovednosti: {', '.join(profile.get('skills', [])) or 'N/A'}",
        f"\nSeniorní role: {', '.join(profile.get('senior_roles', [])) or 'N/A'}",
        f"\nVzdělání: {profile.get('education_level', 'N/A')}",
        f"\nRoky zkušeností: {scores.get('experience_years', 0)}",
        f"\nSeniority skóre: {scores.get('seniority_score', 0)} / 100",
        f"\nOdhad mzdy: {salary['min']}–{salary['max']} CZK / měsíc",
        "\n---\n",
        "Vysvětli, proč takový výsledek vznikl, uveď silné stránky, slabiny a konkrétní doporučení, jak zvýšit mzdu o 30 %.",
    ]
    return "\n".join(prompt)


def _fallback_explanation(profile: dict, scores: dict, salary: dict) -> str:
    strong = []
    if scores['experience_score'] > 20:
        strong.append("silné praktické zkušenosti")
    if scores['skills_score'] > 20:
        strong.append("široký skillset")
    if scores['role_score'] > 10:
        strong.append("seniorní role nebo vedení")
    if scores['education_score'] > 10:
        strong.append("vhodné vzdělání")
    if not strong:
        strong.append("dobrý základ pro další růst")

    weak = []
    if scores['experience_score'] < 15:
        weak.append("doplnit více let kontinuální praxe")
    if scores['skills_score'] < 15:
        weak.append("rozšířit technické dovednosti")
    if scores['role_score'] < 10:
        weak.append("získat více seniorních nebo vedoucích pozic")
    if scores['education_score'] < 10:
        weak.append("posílit vzdělání nebo certifikace")

    recommendations = []
    skills_text = " ".join(profile.get("skills", [])).lower()
    if "cloud" not in skills_text:
        recommendations.append("rozšířit cloudové dovednosti AWS/Azure/GCP a CI/CD automaci")
    if "architecture" not in skills_text and scores['role_score'] < 10:
        recommendations.append("vyhledat příležitosti vést architektonická řešení nebo menší tým")
    if scores['education_score'] < 12:
        recommendations.append("dodat certifikát nebo pokračovat ve formálním vzdělání")
    if not recommendations:
        recommendations.append("zaměřit se na měkké vedení a projevovat větší dopad v projektech")

    return (
        f"Tento kandidát má {', '.join(strong)}. "
        f"Main gapy jsou {', '.join(weak)}. "
        f"Odhad mzdy je {salary['min']}–{salary['max']} CZK měsíčně. "
        f"Pro zvýšení mzdy o 30 % se doporučuje: {recommendations[0]}."
    )

def generate_explanation(profile: dict, scores: dict, salary: dict) -> str:
    prompt = _build_prompt(profile, scores, salary)

    hf_key = os.environ.get(HUGGINGFACE_API_KEY_ENV_VAR)

    if hf_key:
        model = os.environ.get(
            HUGGINGFACE_MODEL_ENV_VAR,
            "deepseek-ai/DeepSeek-R1:fastest"
        )

        try:
            if openai is None:
                raise ImportError(
                    "Package 'openai' není nainstalované. "
                    "Spusť: pip install openai"
                )

            logger.info("Používám HF model: %s", model)

            client = openai.OpenAI(
                base_url="https://router.huggingface.co/v1",
                api_key=hf_key,
            )

            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Jsi zkušený HR a tech recruiter. "
                            "Píšeš stručně, konkrétně a profesionálně."
                        ),
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
                max_tokens=400,
                temperature=0.7,
            )

            text = response.choices[0].message.content

            if text:
                return text.strip()

            logger.warning("HF vrátil prázdnou odpověď.")

        except Exception as exc:
            logger.exception("HF call failed: %s", exc)

    else:
        logger.info(
            "HUGGINGFACE_API_KEY není nastavený. Používám fallback."
        )

    return _fallback_explanation(profile, scores, salary)