$(window).on('load', function() {
	window.fbAsyncInit = function() {
		FB.init({
			appId      : '',
			xfbml      : true,
			version    : 'v2.2'
		});
	};

	(function(d, s, id){
		 var js, fjs = d.getElementsByTagName(s)[0];
		 if (d.getElementById(id)) {return;}
		 js = d.createElement(s); js.id = id;
		 js.src = "//connect.facebook.net/en_US/sdk.js";
		 fjs.parentNode.insertBefore(js, fjs);
	 }(document, 'script', 'facebook-jssdk'));
});

function fb_login(){
	FB.login(function(response) {
		if (response.authResponse) {
			console.log('Fetching your information.... ');
			access_token = response.authResponse.accessToken;
			fb_uid = response.authResponse.userID;
			top.location.href=url+"facebook-login/"+fb_uid+"/"+access_token;
		} else {
			alert('In order to use your Facebook account you need to authorize the Facebook Dialog.');
			console.log('User cancelled login or did not fully authorize.');
		}
	}, {
		scope: 'public_profile,email'
	});
}

function fb_share(){
	FB.ui({
		method: 'share',
		href: 'http://facebook.com',
	}, function(response){
	});
}