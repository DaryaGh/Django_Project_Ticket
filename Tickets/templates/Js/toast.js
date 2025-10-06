document.addEventListener("DOMContentLoaded",function (){
        let toastElList =[].slice.call(document.querySelectorAll('.toast'))
        toastElList.map(function (toastEl){
            let toast = new bootstrap.Toast(toastEl)
            toast.show()
        })
    })