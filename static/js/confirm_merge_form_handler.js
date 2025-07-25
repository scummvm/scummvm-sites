document.getElementById("confirm_merge_form").addEventListener("submit", async function (e) {
  e.preventDefault();

  const form = e.target;

  source_id = form.querySelector('input[name="source_id"]').value
  
  const jsonData = {
    source_id: source_id,
    target_id: form.querySelector('input[name="target_id"]').value,
    options: []
  };
  
  const checkedBoxes = form.querySelectorAll('input[name="options[]"]:checked');
  jsonData.options = Array.from(checkedBoxes).map(cb => {
    const optionData = JSON.parse(cb.value);
    optionData.tick = "on";
    return optionData;
  });
  
  console.log("Data being sent:", jsonData);

  const response = await fetch(`/fileset/${source_id}/merge/execute`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(jsonData),
  });

  if (response.redirected) {
    window.location.href = response.url;
  }
});


function checkForConflicts() {
  const checkedBoxes = document.querySelectorAll('input[name="options[]"]:checked');
  const conflicts = new Map();
  
  Array.from(checkedBoxes).forEach(cb => {
    const option = JSON.parse(cb.value);
    const key = `${option.filename}|${option.prop}`;
    if (!conflicts.has(key)) {
      conflicts.set(key, []);
    }
    conflicts.get(key).push({side: option.side, checkbox: cb});
  });
  
  document.querySelectorAll('input[name="options[]"]').forEach(cb => {
    cb.style.backgroundColor = '';
    cb.parentElement.style.backgroundColor = '';
  });
  
  let hasConflicts = false;
  
  conflicts.forEach((items, key) => {
    if (items.length > 1) {
      
      hasConflicts = true;
      
      items.forEach(item => {
        item.checkbox.style.backgroundColor = '#ffcccc';
        item.checkbox.parentElement.style.backgroundColor = '#ffe6e6';
      });
    }
  });
  
  const submitButton = document.querySelector('button[type="submit"]');
  if (hasConflicts) {
    submitButton.disabled = true;
    submitButton.textContent = 'Resolve Conflicts First';
    submitButton.style.backgroundColor = '#ccc';
  } else {
    submitButton.disabled = false;
    submitButton.textContent = 'Confirm Merge';
    submitButton.style.backgroundColor = '';
  }
}


document.querySelectorAll('input[name="options[]"]').forEach(checkbox => {
  checkbox.addEventListener('change', checkForConflicts);
});

