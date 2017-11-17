var text2="<tr><th>message</th><th>times per day</th></tr>";
var a=['a','b','b','c','a','e','b','c']
var b={};
for(i=0;i<a.length;i++){
  if (a[i] in b){
    b[a[i]]+=1;
  }
  else{
    b[a[i]]=1;

  }
}
//console.log(b);
//console.log(Object.keys(b).length);
for (var key in b){
  var value=b[key];

  text2+="<tr><th>"+key+"</th><th>"+value+"</th></tr>"
}


document.getElementById("table2").innerHTML = text2;
