$(document).ready(function() {
    $("#loading").hide();
    $("#im").hide();
    document.querySelector('#text_to_text_btn').onclick = function() {
        $("#loading").show();
        var text = $("#text_input").val();
        var image = $("#image").val();
        if(text == "" || image == ""){
            alert("Please Enter Something or image is missing");
            $("#loading").hide();
        }else{
            const data = new FormData();
            data.append("upscale", "1");
            data.append("prompt", text);
            data.append("steps", "30");
            data.append("init_image", $('input[type=file]')[0].files[0]);
            data.append("sampler", "euler_a");
            data.append("negative_prompt", "ugly, tiling, poorly drawn hands, poorly drawn feet, poorly drawn face, out of frame, extra limbs, disfigured, deformed, body out of frame, blurry, bad anatomy, blurred, watermark, grainy, signature, cut off, draft");
            data.append("model", "epic_diffusion_1_1");
            data.append("strength", "0.8");
            data.append("guidance", "7");
            const options = {
                method: 'POST',
                headers: {
                    'X-RapidAPI-Key': '3ec1eef879msh365ea5d96552e49p15a7e9jsn95f1d7c21fd9',
                    'X-RapidAPI-Host': 'dezgo.p.rapidapi.com'
                },
                body: data
            };
            fetch('https://dezgo.p.rapidapi.com/image2image', options)
                    .then(response => response.blob())
                    .then(response => {
                        $("#loading").hide();
                        const urlCreator = window.URL || window.webkitURL;
                        var url = urlCreator.createObjectURL(response);
                        $("#im").show();
                        document.getElementById('im').src = url
                    })
                    .catch(err => console.error(err));
        }
    }
});