var gVar;

function init() {

	var searchBox = document.getElementById('searchText'),
		$sBoxObj = $(searchBox);

	searchBox.addEventListener('input',function(e){

		resetResults('Your software libraries search results will appear here!');
		
	});

	$(document).keydown(function(e) {

		if($('#searchText').is(':focus'))
		{
			var keynum;
			
			if(window.event) 
			{ // IE					
            	keynum = e.keyCode;
            }
            else if(e.which)
            { // Netscape/Firefox/Opera					
            	keynum = e.which;
            }
            
	    	if(keynum == 13) 
	    	{ // Enter key is pressed
	        	sendSearchRequest();
	        	return;
	    	}
        }
	    
	});

	$('#searchButton').click(function(i,obj){
		sendSearchRequest();
	});

	setTimeout(function(){
        $sBoxObj.focus();
    }, 1);

}

function resetResults(msg) {
	var resultsContainer = $('#searchResults');
	resultsContainer.empty();
	resultsContainer.append($('<h2/>').html(msg));
}

function sendSearchRequest() {
	var queryText = $("#searchText").val(),
		searchResults = [];
		
	if($.trim(queryText) == '')
		return;

	var startTime = new Date().getTime();
	$('.search-option img').show();

	$.ajax({
		type: "GET",
		url: URL,
		data: {'q': queryText, 'os': $('#targetOSSelect').val(), 'lang': $('#languageSelect').val()}, 
		success: function(data) {
			console.log(JSON.stringify(data));
			gVar = data;
			$('.search-option img').hide();
			if(data){
			    try{
			        searchResults = data["results"];	        
			    }
			    catch(e){
			        alert(e); 
			    }
			}
			else
			{
				resetResults('No results found for '+queryText+'.');
				return;
			}
			var endTime = new Date().getTime();

			resultsContainer = $('#searchResults');
			resultsContainer.empty();
			var resultRow,
				urlTitle = '',
				url = '',
				resultsHeader = $('<div/>').append(
									$('<h3/>')
										.html("Results for <i>"+queryText+"</i> : ")
										.addClass('results-header')
								);
			resultsContainer.append(resultsHeader);

			for(var i = 0; i < searchResults.length; i++) {
				
				url = "https://www.google.com/search?q="+$('#languageSelect').val()+" library "+searchResults[i]['lib_name'];
				urlTitle = searchResults[i]['lib_name'];
				
				var resultRow = $('<div/>').append(
											$('<label/>')
												.append($('<a/>').html(urlTitle).attr('href',url).attr('target',"_blank").addClass(''))
												.addClass('result-title')
								),
					snippetText = 'Used in ',
					snippetRow = $('<p/>').addClass('result-snippet');

					snippetText += searchResults[i]["repo_count"];
					if(parseInt(searchResults[i]["repo_count"]) > 1)
					{
						snippetText += ' repositories'
					}
					else
					{
						snippetText += ' repository'
					}
					snippetRow.html(snippetText);

					resultRow.append(snippetRow)
				
				$(resultRow).hide().appendTo(resultsContainer).fadeIn(i*100);
				//resultsContainer.append(resultRow);
			}
			

			$('#searchText').blur();
		}
	})
}