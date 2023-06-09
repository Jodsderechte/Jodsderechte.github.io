fetch('https://data.wago.io/lookup/wago?id=RaidAbilityTimeline', {
		method: 'get',
		headers: {
			'Content-type': 'application/json'
		},
		body: JSON.stringify(data)
	})
		.then(response => {
			if (!response.ok) {
				throw Error(response.statusText);
			}
			return response.json();
		})
		.then(data => {
      console.log(data)
			data.viewCount
		})
		.catch(error => {
			console.error('Error:', error);
		});
