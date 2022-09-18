console.log("Hello from Admin Users Page!");


async function getUsers() {
    show_load_layout();
    fetch("/user")
    .then(response => response.json())
    .then(data => {
        console.log(data);
        var users_container = document.getElementById("users_rows_container");
        var users_rows = ``

        for (var row = 0; row < data.users.length; row++) {
            var user = data.users[row];
            users_rows += `
                <tr id="${user._id.$oid}">
                    <td>${user.first_name} ${user.last_name}</td>
                    <td>${user.email}</td>
                    <td><input 
                            class="form-check-input" 
                            type="checkbox" 
                            role="switch"
                            onchange="handle_admin_status(event, '${user._id.$oid}')"
                            ${user.roles.includes("admin") && "checked"}
                        >
                    </td>
                    <td><button
                            class="btn btn-close bg-danger"
                            onclick="delete_user(event, '${user._id.$oid}')"
                        ></button>
                    </td>
                </tr>
            `
        }
        users_container.innerHTML = "";
        users_container.innerHTML = users_rows;
        hide_load_layout();
    })
}

// Insert users data into view
getUsers();


function handle_admin_status(e, id){
    var admin = e.currentTarget.checked;

    fetch(`/user/${id}/alter_admin`, {
        method : "PUT",
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({admin})
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
        if (data.success===false && data.error_code === 422) {
            location.reload();
        }
    });
}

function delete_user(e, id) {
    if (confirm('Delete this user?')){
        fetch(`/user/${id}`, {method : "DELETE"})
        .then(response => response.json())
        .then(data => {
            console.log(data);
            if (data.success===true) {
                console.log(document.getElementById(id).remove())
            }
            if (data.success===false && data.error_code === 422) {
                location.reload();
            }
        });
    }
}