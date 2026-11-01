function demoJobs(){
  const skills=document.getElementById("jobSkills").value || "Python";
  document.getElementById("jobResult").innerHTML =
    `<b>Demo results for:</b> ${skills}<br>• Python Developer<br>• Junior Data Analyst<br>• Backend Intern<br><small>Next step: connect a real job API.</small>`;
}
function suggestSkills(){
  const goal=document.getElementById("careerGoal").value || "Data Scientist";
  const map={
    "data scientist":["Python","SQL","Statistics","Pandas","Machine Learning"],
    "web developer":["HTML","CSS","JavaScript","Git","React"],
    "software engineer":["DSA","Java/C++","OOP","DBMS","Git"]
  };
  const key=Object.keys(map).find(k=>goal.toLowerCase().includes(k.split(" ")[1]||k)) || "data scientist";
  document.getElementById("skillResult").innerHTML =
    `<b>Recommended for ${goal}:</b><br>• ${map[key].join("<br>• ")}`;
}
function careerGuide(){
  const q=document.getElementById("careerQuery").value || "career path";
  document.getElementById("guideResult").innerHTML =
    `<b>Demo guidance:</b> For "${q}", start with fundamentals → projects → DSA/interview practice → internships. Connect an AI API later for personalized answers.`;
}
function interviewPrep(){
  const d=document.getElementById("domain").value;
  const questions={
    Java:["What is OOP?","Difference between == and equals()?","Explain inheritance."],
    Python:["List vs tuple?","What are decorators?","Explain dictionary."],
    DSA:["What is a stack?","Array vs linked list?","Explain binary search."],
    "Web Development":["What is DOM?","Flexbox vs Grid?","What is an API?"]
  };
  document.getElementById("interviewResult").innerHTML =
    `<b>${d} Questions</b><br>1. ${questions[d][0]}<br>2. ${questions[d][1]}<br>3. ${questions[d][2]}`;
}


// Show a friendly progress screen while Flask prepares the resume preview.
(function setupResumeProgressScreen(){
  const form = document.getElementById("resumeBuilderForm");
  const overlay = document.getElementById("resumeLoadingOverlay");
  if (!form || !overlay) return;

  const bar = document.getElementById("resumeProgressBar");
  const percent = document.getElementById("resumeProgressPercent");
  const message = document.getElementById("resumeLoadingMessage");
  const stages = [
    { value: 18, text: "Collecting your information…" },
    { value: 38, text: "Organizing education and skills…" },
    { value: 61, text: "Applying your selected template…" },
    { value: 82, text: "Polishing the resume layout…" },
    { value: 92, text: "Almost ready — preparing your preview…" }
  ];
  let isSubmittingAfterAnimation = false;

  form.addEventListener("submit", function(event){
    const submitter = event.submitter;
    if (!submitter || submitter.value !== "preview") return;
    if (isSubmittingAfterAnimation) return;
    if (!form.checkValidity()) return;

    // Pause navigation so the user can actually see the progress animation.
    event.preventDefault();
    overlay.classList.add("is-visible");
    overlay.setAttribute("aria-hidden", "false");
    submitter.disabled = true;
    submitter.textContent = "Building your resume…";

    let stageIndex = 0;
    function advanceStage(){
      const stage = stages[stageIndex++];
      bar.style.width = stage.value + "%";
      percent.textContent = stage.value + "% complete";
      message.innerHTML = '<span class="loading-dot"></span> ' + stage.text;

      if (stageIndex < stages.length) {
        window.setTimeout(advanceStage, 600);
      } else {
        // Keep 92% visible while the actual server request is in progress.
        window.setTimeout(function(){
          isSubmittingAfterAnimation = true;
          form.requestSubmit(submitter);
        }, 450);
      }
    }

    window.requestAnimationFrame(function(){
      window.setTimeout(advanceStage, 180);
    });
  });
})();
