let url = 'https://data.wago.io/lookup/wago?id=RaidAbilityTimeline';
fetch(url, {
		method: 'get',
		headers: {
			'Content-type': 'application/json'
		},
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
