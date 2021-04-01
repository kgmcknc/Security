
function testget(get_data){
   var xmlhttp;
   var object = get_data;
   var valuestring = JSON.stringify(object);
   //alert(valuestring);
   if (window.XMLHttpRequest) {
      xmlhttp = new XMLHttpRequest();
   } else {
      // code for IE6, IE5
      xmlhttp = new ActiveXObject("Microsoft.XMLHTTP");
   }
      xmlhttp.open("GET", "security_proxy.php?q="+valuestring, true);
      xmlhttp.send();
      xmlhttp.onreadystatechange = function() {
      if (this.readyState == 4 && this.status == 200) {
         //document.getElementById(value).innerHTML = this.responseText;
         alert(this.responseText);
      }
   }
}
function testpost(post_data){
   var xmlhttp;
   var object = post_data;
   var valuestring = JSON.stringify(object);
   //alert(valuestring);
   if (window.XMLHttpRequest) {
      xmlhttp = new XMLHttpRequest();
   } else {
      // code for IE6, IE5
      xmlhttp = new ActiveXObject("Microsoft.XMLHTTP");
   }
      xmlhttp.open("POST", "security_proxy.php?q="+valuestring, true);
      xmlhttp.send();
      xmlhttp.onreadystatechange = function() {
      if (this.readyState == 4 && this.status == 200) {
         //document.getElementById(value).innerHTML = this.responseText;
         alert(this.responseText);
      }
   }
}
