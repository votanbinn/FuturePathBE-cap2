document.getElementById("careerForm").addEventListener("submit", function(event) {
    let isValid = true;

    const mbti = document.getElementById("mbti").value;
    if (!mbti.match(/^[A-Z]{4}$/)) {
        document.getElementById("mbtiError").style.display = "block";
        isValid = false;
    } else {
        document.getElementById("mbtiError").style.display = "none";
    }

    const holland = document.getElementById("holland").value;
    if (!holland.match(/^[A-Z]{6}$/)) {
        document.getElementById("hollandError").style.display = "block";
        isValid = false;
    } else {
        document.getElementById("hollandError").style.display = "none";
    }

    const skills = document.getElementById("skills").value;
    if (skills.trim() === "") {
        document.getElementById("skillsError").style.display = "block";
        isValid = false;
    } else {
        document.getElementById("skillsError").style.display = "none";
    }

    const interests = document.getElementById("interests").value;
    if (interests.trim() === "") {
        document.getElementById("interestsError").style.display = "block";
        isValid = false;
    } else {
        document.getElementById("interestsError").style.display = "none";
    }

    if (!isValid) {
        event.preventDefault();
    }
});