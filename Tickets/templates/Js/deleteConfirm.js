document.addEventListener('DOMContentLoaded',function (){
    const deleteBox = document.querySelectorAll('.delete-confirm');

    deleteBox.forEach(link =>{
        link.addEventListener('click',function (e){
            e.preventDefault();
            const confirmation = confirm("Are you sure to delete this Ticket ?");

            if (confirmation){
                window.location.href = this.href;
            }
        })
    })
})