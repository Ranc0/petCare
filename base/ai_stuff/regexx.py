import re
def regex_detector(text):
    matches = {}
    if re.search(r"(drink|thirsty).*(excessive|frequent|constantly)", text):
        matches["increasedthirst"] = 0.9
    if re.search(r"(lost|losing).*weight", text):
        matches["weightloss"] = 0.85
    if re.search(r"(sweet|strange|weird).*(breath|mouth)", text):
        matches["badbreath"] = 0.9
    if re.search(r"(pees|urinates).*(a lot|frequently|excessively)", text):
        matches["increasedurination"] = 0.85
    if re.search(r"(not eating|won.?t eat|refuses food)", text):
        matches["reducedappetite"] = 0.85
    if re.search(r"(pees|urinates).*constantly", text):
        matches["increasedurination"] = 0.9
    if re.search(r"(hungry|always hungry|seems hungry)", text):
        matches["increasedhunger"] = 0.85
    if re.search(r"(breath).*weird", text):
        matches["badbreath"] = 0.9
    if re.search(r"\b(vomit|vomiting|vomits|threw up)\b", text):
        matches["vomiting"] = 0.9
    if re.search(r"\bcollaps(ed|es|ing)\b", text):
        matches["fainting"] = 0.9
    if re.search(r"\b(looks|feels) weak\b", text):
        matches["weakness"] = 0.9
    if re.search(r"(bloody.*diarrhea|bloody.*stool)", text):
        matches["bloodystool"] = 0.9
    if re.search(r"(very tired|extremely tired|completely exhausted)", text):
        matches["fatigue"] = 0.9
    if re.search(r"(wont eat|refuses to eat|not eating)", text):
        matches["reducedappetite"] = 0.9
    if re.search(r"bloody.*(diarrhea|stool)", text):
        matches["bloodystool"] = 0.9

    if re.search(r"(very|extremely|really)\s+tired", text):
        matches["fatigue"] = 0.9

    if re.search(r"(won.?t eat|refuses to eat|not eating at all)", text):
        matches["reducedappetite"] = 0.9
    
    if "diarrhea" in text and "blood" in text:
        matches["bloodystool"] = 0.9
    if re.search(r"no appetite|refuses food|loss of appetite", text):
        matches["reducedappetite"] = 0.9
    if re.search(r"pale gums|gums look pale", text):
        matches["palegums"] = 0.9

    if re.search(r"\b(runny nose|nose.*runny)\b", text):
        matches["nasaldischarge"] = 0.9

    if re.search(r"(sneezes|sneezing|frequent sneezing)", text):
        matches["sneezing"] = 0.9

    if re.search(r"(dazed|confused|not alert|groggy)", text):
        matches["lethargy"] = 0.9

    if re.search(r"(shiver|shivers|shivering)", text):
        matches["shivering"] = 0.9

    if re.search(r"(walking.*odd|walks.*stiff|stiff movements)", text):
        matches["stiffness"] = 0.9
    
    if re.search(r"\b(fever|has a fever|high temperature)\b", text):
        matches["fever"] = 0.9

    if re.search(r"(stiff|stiffness|walking oddly|walks stiffly)", text):
        matches["stiffness"] = 0.9
    
    if re.search(r"(bluish gums|blue gums|gums.*blue)", text):
        matches["cyanosis"] = 0.9

    if re.search(r"(tired quickly|get tired easily)", text):
        matches["fatigue"] = 0.9

    if re.search(r"(labored breathing|breathing.*labored|short of breath)", text):
        matches["laboredbreathing"] = 0.9

    if re.search(r"(whines.*lying down|whines when resting|soft whimper)", text):
        matches["pain"] = 0.9
    
    if re.search(r"(labored breathing|breathing seems labored)", text):
        matches["laboredbreathing"] = 0.9

    if re.search(r"(bluish gums|gums.*blue|gums look blue)", text):
        matches["cyanosis"] = 0.9
    if re.search(r"(tired.*short walk|fatigue.*walking)", text):
        matches["fatigue"] = 0.9

    if re.search(r"(labored.*breathing|breathing.*hard)", text):
        matches["laboredbreathing"] = 0.9

    if re.search(r"(blue.*gums|gums.*blueish|cyanotic gums)", text):
        matches["cyanosis"] = 0.9

    if re.search(r"(whining.*lying down|soft whining|whimper)", text):
        matches["pain"] = 0.9
    if re.search(r"(twitching|random twitch|involuntary movement)", text):
        matches["seizures"] = 0.9

    if re.search(r"(stares.*space|doesn.t respond|blank stare)", text):
        matches["disorientation"] = 0.9

    if re.search(r"(confused|forgets.*command|memory loss)", text):
        matches["cognitiveimpairment"] = 0.9
    
    if re.search(r"(pacing in circles|walks in circles|looping movements)", text):
        matches["Neurological Disorders"] = 0.9

    if re.search(r"(trembles.*touched|twitch when touched)", text):
        matches["highlyexcitable"] = 0.9

    if re.search(r"(snaps at air|invisible things|biting shadows)", text):
        matches["irritable"] = 0.9
    
    if re.search(r"(diarrhea|runny stool|watery poop|loose stools|bloody stool)", text):
        matches["diarrhea"] = 0.9

    if re.search(r"(vomiting|throws up|keeps vomiting|spits up|regurgitating)", text):
        matches["vomiting"] = 0.9

    if re.search(r"(loss of appetite|not eating|refusing food|eats less|no appetite)", text):
        matches["reducedappetite"] = 0.9
    return matches