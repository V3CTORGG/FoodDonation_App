function showNotification(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');

    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;

    document.getElementById('toast-container').appendChild(toast);
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
}

function acceptDonation(donationId) {
    fetch(`/accept_donation/${donationId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Donation accepted successfully', 'success');
            setTimeout(() => location.reload(), 1500);
        } else {
            showNotification('Failed to accept donation', 'danger');
        }
    });
}

function markAsPickedUp(donationId) {
    fetch(`/mark_picked_up/${donationId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Donation marked as picked up', 'success');
            setTimeout(() => location.reload(), 1500);
        } else {
            showNotification('Failed to mark donation as picked up', 'danger');
        }
    });
}

function findReceivers(donationId) {
    fetch(`/find_receivers/${donationId}`)
    .then(response => response.json())
    .then(data => {
        const receiversList = document.getElementById('receiversList');
        receiversList.innerHTML = '';

        if (!data.success) {
            receiversList.innerHTML = '<p class="text-danger text-center">Error finding receivers.</p>';
            showNotification('Error finding receivers.', 'danger');
            return;
        }

        if (data.receivers.length === 0) {
            receiversList.innerHTML = '<p class="text-center">No receivers found nearby.</p>';
        } else {
            data.receivers.forEach(receiver => {
                const receiverId = `receiver-${receiver.id}`;
                receiversList.innerHTML += `
                    <div class="card mb-2">
                        <div class="card-body">
                            <h5 class="card-title">${receiver.name}</h5>
                            <p class="card-text"><strong>Distance:</strong> ${receiver.distance.toFixed(2)} km</p>
                            <div id="${receiverId}-status">
                                <button class="btn btn-primary btn-sm" onclick="sendReceiverRequest(${donationId}, ${receiver.id})">
                                    Send Request
                                </button>
                            </div>
                        </div>
                    </div>
                `;
            });
        }

        new bootstrap.Modal(document.getElementById('receiversModal')).show();
    })
    .catch(error => {
        showNotification('Server error while finding receivers.', 'danger');
        console.error('Error:', error);
    });
}

function sendReceiverRequest(donationId, receiverId) {
    fetch(`/send_request/${donationId}/${receiverId}`, { method: 'POST' })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            document.getElementById(`receiver-${receiverId}-status`).innerHTML = '<span class="badge bg-success">Request Sent</span>';
            showNotification('Request sent successfully.', 'success');
        } else {
            showNotification('Failed to send request.', 'danger');
        }
    })
    .catch(error => {
        showNotification('Error sending request.', 'danger');
        console.error('Error:', error);
    });
}
function assignReceiver(donationId, receiverId) {
    fetch(`/assign_receiver/${donationId}/${receiverId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Receiver assigned successfully', 'success');
            // Update route on map from NGO location to receiver
            const receiver = data.receiver;
            showRoute(data.ngo_lat, data.ngo_lng, receiver.latitude, receiver.longitude);
            setTimeout(() => location.reload(), 1500);
        } else {
            showNotification('Failed to assign receiver', 'danger');
        }
    });
}

