import numpy as np
import random as rd
from scipy.stats import beta
import plotly as py

class Simulator:
    def __init__(self, n_machines, n_iters, probabilities=None, cmap=py.colors.qualitative.D3):
        self.cmap = cmap
        self.probabilities = probabilities
        self.n_machines = n_machines
        self.n_iters = n_iters
        self.probs = None
        self.iter = 0
        
        self.machines = None
        self.colors = None
        self.line_colors = None
    
    def simulate(self):
        
        if self.probabilities is None:
            self.probs = [rd.random() for i in range(self.n_machines)]
        else:
            self.probs = self.probabilities
        
        self.results= []
        #self.count = [[[0,0]] for i in range(self.n_machines)]
        self.count = np.zeros((self.n_machines, self.n_iters+1, 2), dtype=int)
        
        for i in range(self.n_iters):
            self.iter = i
            m = self.select_machine()
            success = rd.random() < self.probs[m]
            
            for j in range(self.n_machines):
                if j == m:
                    self.count[m,i+1,0] = self.count[m,i,0] + success
                    self.count[m,i+1,1] = self.count[m,i,1] + 1-success
                else:
                    self.count[j,i+1,0] = self.count[j,i,0]
                    self.count[j,i+1,1] = self.count[j,i,1]
                    

            self.results.append((m, success))
            
    def _main_plot(self, frame=None, just_data=False):
        if frame is None:
            frame = self.n_iters
        if self.machines is None:
            self.machines = np.array([r[0]+1 for r in self.results])
        if self.colors is None:
            self.colors = np.array([self.cmap[r[0]] if r[1] else "white"  for r in self.results])
        if self.line_colors is None:
            self.line_colors = np.array([self.cmap[r[0]]  for r in self.results])
        
        scatter_dict = {"x": np.arange(frame),
                        "y": self.machines[:frame],
                        "marker": {"color": self.colors,
                                   "size" : 10,
                                   "line" : {"color": self.line_colors,
                                             "width": 2}}}
        if not just_data:
            scatter_dict["mode"] = "markers"
            scatter_dict["hoverinfo"] = "none"
            scatter_dict["name"] = "id"
        
        plot = py.graph_objs.Scatter(**scatter_dict)
        
        return plot
    
    def _log_range(self,n_points):
        LOG10_5 = np.log10(.5)

        r = np.zeros(n_points)
        r[-1] = 1

        t = np.logspace(-5, LOG10_5, n_points//2-1, endpoint=False)
        r[1           :(n_points//2)    : 1] = t
        r[(n_points-2):((n_points-1)//2):-1] = 1 - t
        
        if n_points % 2 == 1:
            r[n_points//2] = .5
        
        return r

    def _machines_plot(self, i, n_points=101, frame=None, just_data=False):
        if frame is None:
            frame = self.n_iters-1

        qs = self._log_range(n_points)
        xs = beta.ppf(qs, a=self.count[i,frame,0]+1, b=self.count[i,frame,1]+1)
        ys = beta.pdf(xs, a=self.count[i,frame,0]+1, b=self.count[i,frame,1]+1)
        ys /= np.max(ys)

        scatter_dict = {"x": xs,
                        "y": ys}
        
        if not just_data:
            scatter_dict["fill"]  = "tozeroy"
            scatter_dict["line"]  = {"shape": "spline",
                                     "color": self.cmap[i]}
            scatter_dict["name"]  = f"θ<sub>{i+1}</sub>"
            scatter_dict["xaxis"] = "x" + str(i+1)
            scatter_dict["yaxis"] = "y" + str(i+1)
        
        plot = py.graph_objs.Scatter(**scatter_dict)
        
        return plot
    
    def _all_machines_plot(self, n_points=101, frame=None, just_data=False):
        if frame is None:
            self.n_iters-1
        return [self._machines_plot(i,
                                    n_points=n_points,
                                    frame=frame,
                                    just_data=just_data)
                for i in range(self.n_machines)]
    
    def _layout(self):
        margin = 0.025
        step = 1/self.n_machines
        
        layout_xs = {"xaxis" + str(i): {"domain": [step*(i-1)+margin, step*i-margin],
                                        "anchor": "y"+str(i)} 
                     for i in range(1,1+self.n_machines)}
        layout_ys = {"yaxis" + str(i): {"domain": [0, .5-margin],
                                        "range": [0, 1.05],
                                        "anchor": "x"+str(i)} 
                     for i in range(1, 1+self.n_machines)}
        idx = self.n_machines+1        
        layout_main = {"xaxis" + str(idx): {"domain": [0, 1],
                                            "range": [-3, 100],
                                            "anchor": "y"+str(idx),},
                       "yaxis" + str(idx): {"domain": [0.5+margin, 1],
                                            "range": [.8, self.n_machines+0.2],
                                            "anchor": "x"+str(idx),
                                            "tickmode": "array",
                                            "tickvals": np.arange(1,self.n_machines+1),
                                            "ticktext": [f"{i+1}<br>p={round(self.probs[i],2)}" for i in range(self.n_machines)]}}
        layout = {**layout_xs, **layout_ys, **layout_main}

        return layout
    
    def _full_plot(self):
        #get layout
        layout = self._layout()
        
        #get data of all machines and set the axis
        machine_plots = self._all_machines_plot()
        
        #get data of main plot and set the axis
        idx = self.n_machines+1
        main_plot = self._main_plot()
        
        main_plot["xaxis"] = "x"+str(idx)
        main_plot["yaxis"] = "y"+str(idx)
        
        #merge data
        data = [main_plot, *machine_plots]
        
        #plot
        py.offline.iplot({"data":data, "layout": layout})
        
    def animation(self):
        # make figure
        fig_dict = {
            "data": [],
            "layout": {},
            "frames": []
        }
        
        machines_plots = self._all_machines_plot(frame=0)

        main_plot = self._main_plot(frame=0)
        idx = self.n_machines+1
        main_plot["xaxis"] = "x"+str(idx)
        main_plot["yaxis"] = "y"+str(idx)

        fig_dict["data"] = [main_plot, *machines_plots]
        
        
        fig_dict["layout"] = self._layout()
        
        fig_dict["layout"]["updatemenus"] = [
            {
                "buttons": [
                    {
                        "args": [None, {"frame": {"duration": 500, "redraw": False},
                                        "fromcurrent": True, "transition": {"duration": 300,
                                                                            "easing": "quadratic-in-out"}}],
                        "label": "Play",
                        "method": "animate"
                    },
                    {
                        "args": [[None], {"frame": {"duration": 0, "redraw": False},
                                          "mode": "immediate",
                                          "transition": {"duration": 0}}],
                        "label": "Pause",
                        "method": "animate"
                    }
                ],
                "direction": "left",
                "pad": {"r": 10, "t": 87},
                "showactive": False,
                "type": "buttons",
                "x": 0.1,
                "xanchor": "right",
                "y": 0,
                "yanchor": "top"
            }
        ]

        sliders_dict = {
            "active": 0,
            "yanchor": "top",
            "xanchor": "left",
            "currentvalue": {
                "font": {"size": 20},
                "prefix": "Iteration:",
                "visible": True,
                "xanchor": "right"
            },
            "transition": {"duration": 300, "easing": "cubic-in-out"},
            "pad": {"b": 10, "t": 50},
            "len": 0.9,
            "x": 0.1,
            "y": 0,
            "steps": []
        }
        
        # make frames
        for i in range(0,self.n_iters+1):
            frame = {"name": str(i)}

            machines_plots = self._all_machines_plot(frame=i, just_data=True)

            main_plot = self._main_plot(frame=i, just_data=True)
            idx = self.n_machines+1
            main_plot["xaxis"] = "x"+str(idx)
            main_plot["yaxis"] = "y"+str(idx)
            
            frame["data"] = [main_plot, *machines_plots]    
            
            fig_dict["frames"].append(frame)
            slider_step = {"args": [
                [i],
                {"frame": {"duration": 300, "redraw": False},
                 "mode": "immediate",
                 "transition": {"duration": 300}}
            ],
                "label": i,
                "method": "animate"}
            sliders_dict["steps"].append(slider_step)


        fig_dict["layout"]["sliders"] = [sliders_dict]
        
        py.offline.iplot(fig_dict, auto_play=False)

    def regret(self):
        mu_optimal = np.max(self.probs)
        
        mus = np.array(self.probs)[[i[0] for i in self.results]]

        return mu_optimal - mus

    def cumulative_regret(self):
        return np.cumsum(self.regret())