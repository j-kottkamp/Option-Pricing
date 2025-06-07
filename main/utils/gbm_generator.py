from imports import np, plt, time, os, st

def geometric_brownian_motion(S0=100, mu=0.07, sigma=0.2, T=1, n_sims=10000000):
    '''
    Older Version, RAM intensive.
    Broke browser at 5Mio+ paths. 
    Use at own risk and only if RAM>32Gb.
    '''
    n_steps = int(T * 252)
    dt = 1 / n_steps
    Z = np.random.standard_normal((n_steps, n_sims))
    increments = ((mu - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * Z)
    log_returns = np.vstack([np.zeros(n_sims), increments.cumsum(axis=0)])
    S = S0 * np.exp(log_returns)
    return S

def gbm_memmap(S0=100, mu=0.07, sigma=0.2, T=1, n_sims=100000):
    '''
    Recent Version. 
    Iterate over paths to minimize RAM usage. Creates file 'gbm_paths.dat' in data folder.
    To access data without loading the full file, use np.memmap().
    Must contain ".flush()" and "del." after. Otherwise file wont be closed.
    '''
    n_steps = int(T * 252)
    dt = 1 / n_steps
    
    # Go into main and into "data"  
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(os.path.dirname(base_dir), "data")

    file_path = f"{data_dir}\\gbm_paths.dat"
    try: 
        # Create new file and/or rewrite it
        S = np.memmap(filename=file_path, dtype="float32", mode="w+", shape=(n_sims, n_steps + 1))
    except: 
        # Only rewrite it. If user reloads while "gbm_paths.dat" still accessed by previous functions
        S = np.memmap(filename=file_path, dtype="float32", mode="r+", shape=(n_sims, n_steps + 1))
        
    S[:, 0] = S0

    bar = st.progress(0, text="Generating GBM Paths")
    for t in range(1, n_steps + 1):
        z = np.random.standard_normal(size=(n_sims))
        
        S[:, t] = S[:, t - 1] * np.exp((mu - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * z)

        try:
            bar.progress(t)
        except:
            pass
    
    S.flush()
    del S

    return n_steps, file_path


if __name__ == "__main__":
    start = time.time()
    gbm_memmap()
    end = time.time()
    print(f"Time taken: {end - start} seconds")
