import os
from flask import Flask, request, jsonify, send_from_directory
from together import Together
import difflib
import json

app = Flask(__name__)

TOGETHER_API_KEY = os.environ.get("TOGETHER_API_KEY")
MODEL = "meta-llama/Llama-Vision-Free"  # Make sure this is the correct model you have access to

client = Together(api_key=TOGETHER_API_KEY)

faq = {
    "what is 48 digital": "48 Digital is a results-driven digital marketing agency offering a full suite of services including SEO, SMM, PPC, ORM, Web Design, AI-driven Voice Search Marketing, UI/UX Design, and Social Media Content Management.",
    "who are your ideal clients": "We work with startups, small businesses, and enterprises across industries who want to grow their online presence, drive traffic, and generate leads or conversions.",
    "services offered": "We offer Search Engine Optimization (SEO), Social Media Marketing (SMM), Pay Per Click Advertising (PPC), Website Design, Voice Search & AI Marketing, UI/UX Design, and Online Reputation Management (ORM).",
    "what services do you offer": "We offer SEO, SMM, PPC, Web Design, Voice Search & AI Marketing, UI/UX Design, and ORM.",
    "seo": "Our SEO services include website audit and on-page optimization, keyword research, technical SEO, backlink building, local SEO, and content optimization with blog strategy.",
    "what does your seo service include": "Our SEO services include website audit and on-page optimization, keyword research, technical SEO, backlink building, local SEO, and content optimization and blog strategy.",
    "how long does it take to see seo results": "Typically, noticeable improvements take 3–6 months, depending on competition and the current state of your website.",
    "smm": "We manage Instagram, Facebook, LinkedIn, X (formerly Twitter), TikTok, and YouTube.",
    "what platforms do you manage": "We manage Instagram, Facebook, LinkedIn, X (formerly Twitter), TikTok, and YouTube.",
    "what's included in social media management": "Social media management includes strategy planning, post creation (images, videos, captions), scheduling and publishing, community engagement, and monthly analytics reports.",
    "ppc": "We run campaigns on Google Ads (Search, Display, YouTube), Facebook & Instagram Ads, LinkedIn Ads, and TikTok Ads.",
    "what ppc platforms do you use": "We run campaigns on Google Ads (Search, Display, YouTube), Facebook & Instagram Ads, LinkedIn Ads, and TikTok Ads.",
    "what's included in your ppc service": "Our PPC service includes keyword research and ad strategy, ad creation and targeting, A/B testing, budget optimization, and weekly performance tracking.",
    "web design": "We design business websites, landing pages, portfolio sites, e-commerce platforms (Shopify, WooCommerce), and CMS-based websites (WordPress, Webflow).",
    "what type of websites do you build": "We design business websites, landing pages, portfolio sites, e-commerce platforms (Shopify, WooCommerce), and CMS-based websites (WordPress, Webflow).",
    "do you offer hosting or domain registration": "We can assist in setup and connect you with trusted providers, but we do not directly sell domains or hosting.",
    "orm": "We manage online reputation through review monitoring and response strategy, Google My Business optimization, press releases and positive content strategy, and removal or suppression of negative search results (if possible).",
    "how do you manage online reputation": "We manage online reputation through review monitoring and response strategy, Google My Business optimization, press releases and positive content strategy, and removal or suppression of negative search results (if possible).",
    "voice search marketing": "Voice Search Marketing is the process of optimizing your digital content so it ranks in voice-based searches made via assistants like Siri, Alexa, or Google Assistant.",
    "what is voice search marketing": "Voice Search Marketing is the process of optimizing your digital content so it ranks in voice-based searches made via assistants like Siri, Alexa, or Google Assistant.",
    "why is voice search important": "More users are searching using voice — especially on mobile — and being voice-ready gives your brand an edge in discoverability.",
    "ui ux design": "Our UI/UX design services include wireframing and prototyping, user journey mapping, mobile-first design, UX audits of existing sites, and responsive, accessible interfaces.",
    "what is included in ui ux design services": "Our UI/UX design services include wireframing and prototyping, user journey mapping, mobile-first design, UX audits of existing sites, and responsive, accessible interfaces.",
    "how do i get started": "Simply book a free consultation or contact us through our website. We’ll assess your goals and suggest the best strategy.",
    "do you offer monthly retainers": "Yes. Most clients choose monthly packages for SEO, SMM, and PPC. We also offer one-time projects such as website design or social media posts.",
    "how do you measure success": "We provide monthly reports with key KPIs such as website traffic, conversion rates, engagement metrics, and ROI on paid campaigns.",
    "contact information": "You can email us at info@foureight.digital or use the form on our website.",
    "what is your email": "info@foureight.digital",
    "where are you located": "Our office is based in Dubai, United Arab Emirates. Avenue Residence – Building 2, Floor 4.",
    "location": "Our office is based in Dubai, United Arab Emirates. Avenue Residence – Building 2, Floor 4.",
    "business hours": "Our office is open 7am to 7pm UAE Time. Support agents are available 24/7.",
    "support hours": "Support agents are available 24/7.",
    "how much": "Pricing depends on your needs. Please contact us for a custom quote or to discuss your project.",
    "how much does it cost": "Pricing depends on your needs. Please contact us for a custom quote or to discuss your project.",
    "what is your pricing": "We offer custom packages based on your goals. Contact us for a free consultation and quote.",
    "pricing": "We offer custom packages based on your goals. Contact us for a free consultation and quote at info@foureight.digital",
    "cost": "Pricing depends on your needs. Please contact us for a custom quote or to discuss your project.",
    "what is ur name": "I am the 48 Digital chatbot, here to assist you with your inquiries.",
    "name": "I am the 48 Digital chatbot, here to assist you with your inquiries.",
    "who are you": "I am the 48 Digital chatbot, here to assist you with your inquiries.",
    "what can you do": "I can answer questions about our services, pricing, and help you get in touch with our team.",
    "how can i contact you": "You can email us at info@foureight.digital or use the form on our website.",
    "contact": "You can email us at info@foureight.digital or use the form on our website."
}

instructions = """
Only answer questions about 48 Digital, its services, pricing, or contact information. 
If the question is not about 48 Digital, say: 'Sorry, I can only answer questions about 48 Digital.'
Keep answers brief and friendly.
You can use emojis to make responses more engaging.
"""

def find_best_faq_match(user_msg, faq_dict, threshold=0.7):
    questions = list(faq_dict.keys())
    match = difflib.get_close_matches(user_msg, questions, n=1, cutoff=threshold)
    if match:
        return faq_dict[match[0]]
    # Try partial match as fallback
    for q in questions:
        if user_msg in q or q in user_msg:
            return faq_dict[q]
    return None

@app.route("/")
def home():
    return send_from_directory("static", "index.html")


@app.route("/chat", methods=["POST"])
def chat():
    user_msg = request.json.get("message", "").lower().strip()
    print(f"Received message: {user_msg}")

    # 1. Try FAQ (fuzzy and partial match)
    faq_answer = find_best_faq_match(user_msg, faq)
    if faq_answer:
        return jsonify({"reply": faq_answer + " 🤖"})

    # 2. Otherwise, use the AI model
    messages = [
        {"role": "system", "content": instructions},
        {"role": "user", "content": user_msg}
    ]

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
        )
        reply = response.choices[0].message.content.strip()

        # Remove trailing tokens if any
        if "<|im_start|>" in reply:
            reply = reply.split("<|im_start|>")[0].strip()

        # Fallback if model returns empty
        if not reply:
            reply = "Sorry, I can only answer questions about 48 Digital."

        return jsonify({"reply": reply})

    except Exception as e:
        print(f"AI error: {e}")
        return jsonify({"reply": "Sorry, there was an error processing your request."})


@app.route("/feedback", methods=["POST"])
def feedback():
    data = request.get_json()
    user = data.get("user")
    message = data.get("message")
    feedback_val = data.get("feedback")
    print(f"Feedback from {user}: {feedback_val} for '{message}'")
    with open("feedback_log.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(data) + "\n")
    return "", 204


if __name__ == "__main__":
    app.run()