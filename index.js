const express =require('express');
const app= express();
const port= 3005;
const path = require('path');


app.get('/', (req,res)=>{
    res.sendFile(path.join(__dirname, 'public', 'home.html'));
})
app.get('/verity', (req,res)=>{
    res.sendFile(path.join(__dirname, 'public', 'Verify.html'));
})
app.listen(port,()=>console.log('Welcome to VerityVault'));