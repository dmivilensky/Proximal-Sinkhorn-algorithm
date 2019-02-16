import scipy.stats as stats
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

import numpy as np
import math
from PIL import Image
import matplotlib.pyplot as plt
from tqdm import tqdm


class Experiments:
    @staticmethod
    def load_image(filename, basewidth):
        img = Image.open(filename)
        wpercent = (basewidth / float(img.size[0]))
        hsize = int((float(img.size[1]) * float(wpercent)))
        img = img.resize((basewidth, hsize), Image.ANTIALIAS)
        return np.asarray(img, dtype="int32")

    @staticmethod
    def load_data(img1_path='1.png', img2_path='2.png', show=False, size=10):
        img1 = Experiments.load_image(img1_path, size)
        img2 = Experiments.load_image(img2_path, size)

        C = np.zeros((img1.shape[0] * img1.shape[1], img1.shape[0] * img1.shape[1]))

        for i in range(img1.shape[0] * img1.shape[1]):
            for j in range(img1.shape[0] * img1.shape[1]):
                C[i, j] = np.linalg.norm(np.array([i // img1.shape[0], i % img1.shape[1]]) - np.array([j // img1.shape[0], j % img1.shape[1]]), 2)

        img1 += 1
        img2 += 1
        p = img1.reshape((img1.shape[0] * img1.shape[1], )) / np.sum(img1)
        q = img2.reshape((img2.shape[0] * img2.shape[1], )) / np.sum(img2)

        if show:
            plt.figure()
            plt.subplot(121)
            plt.imshow(img1, cmap='gray')
            plt.subplot(122)
            plt.imshow(img2, cmap='gray')
            plt.show()
        return C, p, q
    
    @staticmethod
    def visualize_x(x, n):
        plt.imshow(x.reshape(int(math.sqrt(n)), int(math.sqrt(n)), n).sum(2))
    
    @staticmethod
    def test(problems, config=None, methods=None):
        config = config or {'eps': (0.01, 0.01, 1), 'gamma': (10, 0.01, 2)}
        methods = methods or []
        epsilons = [config['eps'][0] / config['eps'][2]**i for i in range(int(math.log(config['eps'][0] / config['eps'][1], config['eps'][2] + 1e-5)) + 1)]
        gammas = [config['gamma'][0] / config['gamma'][2]**i for i in range(int(math.log(config['gamma'][0] / config['gamma'][1], config['gamma'][2] + 1e-5)) + 1)]

        iterations = [[] for i in range(len(methods))]

        with tqdm(total=len(epsilons) * len(gammas) * len(methods) * len(problems)) as ph:
            for (C, p, q) in problems:
                for eps in epsilons:
                    for gamma in gammas:
                        for i, method in enumerate(methods):
                            _, iterations_num, _ = method(C, p, q, gamma, eps)
                            iterations[i].append(iterations_num)
                            ph.update(1)
            
        return np.array(epsilons), np.array(gammas), np.array(iterations).reshape((len(epsilons), len(methods), len(problems), len(gammas)))
    
    @staticmethod
    def plot_algorithm_comparation(gammas, iterations, epsilon, n, methods_names=None):
        iters = iterations[0,:,0,:].reshape(1,-1).T
        epss = gammas
        n_methods = len(methods_names or [])
        
        df = pd.DataFrame()
        df.insert(0, "gamma", epss.tolist() * n_methods)
        df.insert(1, "N", iters)
        df.insert(0, "methods", list(sum([[name] * len(epss) for i, name in enumerate(methods_names or [])], [])))
        
        sns.set(style="ticks")
        lm = sns.lineplot(x="gamma", y="N", hue="methods",
                        data=df)
        lm.set(xlabel='$\gamma$', ylabel='$N(\epsilon, \gamma)$',
               title="$N(\epsilon, \gamma), \epsilon = %.2f$" % (epsilon))
    
    @staticmethod
    def plot_algorithm_comparation_pyplot(gammas, iterations, epsilon, n, gamma_star, save=False, methods_names=None):
        iters = iterations[0,:,0,:].reshape(1,-1).T
        epss = gammas
        n_methods = len(methods_names or [])
        
        plt.plot(epss.tolist() * n_methods, iters)
        plt.xlabel("$\gamma$")
        plt.ylabel("$N(\epsilon, \gamma)$")
        plt.title("$N(\epsilon, \gamma), \epsilon = %.2f$" % (epsilon) + "\n" + ", ".join(methods_names))
        
        plt.plot([gamma_star, gamma_star], [0, np.max(iters)], "r:", label="$\gamma^* = %.2e$" % gamma_star)
        gamma = 0
        for i in range(iters.shape[0]-1, 1, -1):
            if iters[i][0] / iters[i-1][0] > 1.36:
                gamma = epss[i]
                break
        plt.plot([gamma, gamma], [0, np.max(iters)], "g:", label="$\gamma = %.2e$" % gamma)
        if save:
            plt.savefig("plot_algorithm_comparation_pyplot.png", dpi=800)
        
        plt.legend()
       
    @staticmethod
    def plot_algorithm_log_comparation(gamma, iterations, epsilons, n, methods_names=None):
        iters = np.log(iterations[:,:,0,0].reshape(1,-1).T)
        epss = np.log(1/epsilons)
        n_methods = len(methods_names or [])
        
        slope = [stats.linregress(epss, iters[len(epss)*i:len(epss)*(i+1)].reshape(len(epss)))[0] for i in range(n_methods)]
        
        df = pd.DataFrame()
        df.insert(0, "log(1/eps)", epss.tolist() * n_methods)
        df.insert(1, "log(N)", iters)
        df.insert(0, "methods", list(sum([[name + ", $ϰ_%i = %.2f$" % (i+1, slope[i])] * len(epss) for i, name in enumerate(methods_names or [])], [])))
        
        sns.set(style="ticks")
        lm = sns.lmplot(x="log(1/eps)", y="log(N)", hue="methods",
                        data=df, legend=False,
                        height=8, aspect=(1+np.sqrt(5))/2)
        lm.set(xlabel='$log(1 / \epsilon)$', ylabel='$log\;N(\epsilon, \gamma)$',
               title="$log\;N(\epsilon, \gamma), \gamma = %.2f$" % (gamma))
        lm.ax.legend(bbox_to_anchor=(0.3, 1, 0., .0), loc=0,
                     ncol=1, borderaxespad=0.)
        plt.savefig("plot_algorithm_log_comparation.png", dpi=800)
        
    