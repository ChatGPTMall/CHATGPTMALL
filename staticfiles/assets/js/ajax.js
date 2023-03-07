window.onload = initall;
var saveAnsButton;
var saveAnsButtonLast = document.getElementById("save_ans_last");
saveAnsButtonLast.addEventListener("click", (e)=>{
    calculate_submission();
    submit_user_answers()
    localStorage.removeItem("questions")
    localStorage.removeItem("answers")
})

function initall(){
 saveAnsButton = document.getElementById("save_ans");
 saveAnsButton.onclick = calculate_submission
}


function calculate_submission(){
    var answers = new Array();
    var questions = new Array();
    var answer = $('.quiz:checked').val();
    var question = $("#question_id").val();

    var local_questions = localStorage.getItem("questions")
    var local_answers = localStorage.getItem("answers")
    if(local_questions && local_questions){
        local_questions = JSON.parse(local_questions)
        local_answers = JSON.parse(local_answers)
        local_questions.push(question)
        local_answers.push(answer)
        localStorage.setItem("questions", JSON.stringify(local_questions))
        localStorage.setItem("answers", JSON.stringify(local_answers))
    }
    else{
        answers.push(answer)
        questions.push(question)
        localStorage.setItem("questions", JSON.stringify(questions))
        localStorage.setItem("answers", JSON.stringify(answers))

    }

}

function submit_user_answers(){
    var user = $("#user").val();
    var quiz_id = $("#quiz_id").val();
    var final_questions = localStorage.getItem("questions")
    var final_answers = localStorage.getItem("answers")
    console.log(final_questions, final_answers)
    var req = new XMLHttpRequest();
    var url = `/api/student/quiz/submissions/?final_answers=${final_answers}&user=${user}&quiz_id=${quiz_id}&final_questions=${final_questions}`
    req.open("GET", url, true)
    req.send()
}

function ajaxMarkProgress(id){
    var req = new XMLHttpRequest();
    var url = `/api/student/watched/${id}/`
    req.open("GET", url, true)
    req.send()
}