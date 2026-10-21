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
