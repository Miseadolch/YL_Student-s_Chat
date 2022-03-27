function updateImage(){
    if (this.files && this.files.length){
        preview.src = window.URL.createObjectURL(this.files[0]);
    }else{
        preview.src = "static/img/etot_parol_nikto_ne_uznaet.png";
    }
}

function highlightDropZone(event){
    event.preventDefault();
    this.classList.add('drop');
}

function unHighlightDropZone(event){
    event.preventDefault();
    this.classList.remove('drop');
}


const input = document.getElementById('avatar');
const preview = document.getElementById('preview');
const dropFiles = document.getElementsByClassName("avatar-field");

if (dropFiles && dropFiles.length){
    const dropField = dropFiles[0];
    dropField.addEventListener('dragover', highlightDropZone);
    dropField.addEventListener('dragenter', highlightDropZone);
    dropField.addEventListener('dragleave', unHighlightDropZone);
    dropField.addEventListener('drop', (event) => {
        const dt = event.dataTransfer;
        unHighlightDropZone.call(dropField, event)
        updateImage.call(dt);
    });
}

input.addEventListener('change', updateImage);
