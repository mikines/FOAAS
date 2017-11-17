


// what we shoud do in final project is just replace 'a' by the existing
//number in the user's account
var a=[1,2,3,4,5]
var text="<tr align='left'><th>your registered messsage:</th></tr>";
var i;
for (i=0; i<a.length;i++){
  text+= "<tr align='right'><td>"+a[i]+"</td></tr>";
}
text+="<tr><td><input type='text' placeholder='enter new number'><button id ='add' type='submit'>Add a number</button></td></tr>"
document.getElementById("table1").innerHTML = text;
