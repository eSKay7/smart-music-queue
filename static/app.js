const $ = id => document.getElementById(id)

let countdownTimer = null;
let songStartTime = null;

async function api(path, method="GET", body=null){
    const options = {method, headers:{"Content-Type": "application/json"}};
    if (body){
        options.body = JSON.stringify(body);
    }
    const res = await fetch(`/api/${path}`, options);
    if (!res.ok){
        const errortext = await res.text();
        throw new Error(`API ${path} failed: ${res.status} ${errortext}`);
    }
    return res.json();
}

function setStatus(message){
    $('status').textContent = message || '';
}

async function loadPlaylists(){
    try{
        const data = await api('playlists');
        const select = $('playlistSelect');
        select.innerHTML = '';
        if (Array.isArray(data)){
            data.forEach(pl => {
                const option = document.createElement('option');
                option.value = pl.id ?? pl;
                option.textContent = pl.name ?? `Playlist ${pl.id ?? pl}`;
                select.appendChild(option);
            });
        }
        setStatus('Playlists loaded');
    }
    catch(err){
        setStatus('Could not load playlists: ' + err.message)
    }
}

async function refreshState(){
    try{    
        const state = await api('state');
        renderState(state);
        setStatus('State Refreshed');
    }
    catch(err){
        setStatus('Could not refresh state: ' + err.message)
    }
}

function renderState(state){
    $('currentSong').textContent = state.current_song ?? '-';
    const q = $('queueList');
    q.innerHTML = '';
    (state.queue || []).forEach(song =>{
        const li = document.createElement('li');
        li.textContent = String(song);
        q.appendChild(li);
    });
    if (state.playing){
        songStartTime = Date.now() - ((state.elapsed || 0) * 1000);
        startCountdown();
    }
    else{
        stopCountdown();
    }
}

async function startPlay(){
    const playlistId = $('playlistSelect').value;
    try{
        await api('play', 'POST', {playlist_id: playlistId});
        setStatus('Playback started');
        await refreshState();
    }
    catch(err){
        setStatus('Could not start playback: ' + err.message)
    }
}

async function startCountdown(){
    stopCountdown();
    const interval = 20;
    const total = interval;
    countdownTimer = setInterval(() => {
        const elapsed = (Date.now() - (songStartTime || Date.now())) / 1000;
        const remaining = Math.max(0, Math.round((total - elapsed) * 10) / 10);
        $('countdown').textContent = `${remaining}s`;
        if (remaining <= 0){
            if ($('autoplayToggle').checked){
                doSkip(/*User initiated = */false, /*Auto incremented = */true);
            }
            else{
                stopCountdown();
            }
        }
    }, 200);
}

async function stopCountdown(){
    if (countdownTimer){
        clearInterval(countdownTimer);
        countdownTimer = null;
        $('countdown').textContent = '-';
    }
}

async function doShuffle(){
    try{
        await api('shuffle', 'POST');
        await refreshState();
        setStatus('Playlist shuffled')
    }
    catch(err){
        setStatus('Could not shuffle playlist: ' + err.message)
    }
}

async function toggle(){
    try{
        await api('toggle', 'POST');
        await refreshState();
        setStatus('Toggled play/pause');
    }
    catch(err){
        setStatus('Could not toggle play/pause ' + err.message)
    }
}

async function doSkip(userInitiated=true){
    const elapsed = (Date.now() - (songStartTime || Date.now())) / 1000;
    const early = userInitiated && elapsed <= 5;
    try{
        await api('skip', 'POST', {early: early});
        setStatus(`Skipped (early=${early})`);
        await refreshState();
    }
    catch(err){
        setStatus('Could not skip: ' + err.message);
    }
}

async function doAdd(){
    const s = $('songInput').value;
    if (!s) {
        return setStatus('Enter a song to add');
    }
    try{
        await api('add', 'POST', {queue_song: Number(s)})
        setStatus('Added ' + s);
        await refreshState();
    }
    catch(err){
        setStatus('Could not add: ' + err.message);
    }
}

async function doRemove(){
    const s = $('songInput').value;
    if (!s) {
        return setStatus('Enter a song to remove');
    }
    try{
        await api('remove', 'POST', {dequeue_song: Number(s)})
        setStatus('Removed ' + s);
        await refreshState();
    }
    catch(err){
        setStatus('Could not remove: ' + err.message)
    }
}

document.addEventListener('DOMContentLoaded', async () => {
    $('playbtn').addEventListener('click', startPlay);
    $('playpause').addEventListener('click', toggle);
    $('skip').addEventListener('click', () => doSkip(true));
    $('addsong').addEventListener('click', doAdd);
    $('removesong').addEventListener('click', doRemove);
    $('shufflebtn').addEventListener('click', doShuffle);

    $('autoplayToggle').addEventListener('change', e => {
        if(e.target.checked) startCountdown();
        else stopCountdown();
    });

    await loadPlaylists();
    await refreshState();

    setInterval(refreshState, 5000);
})