(ns kmeans.kmeans
  (:gen-class)
  (:require [clojure.core.matrix :as m]
            [clojure.data.csv :as csv]
            [mikera.image.core :as image]
            [mikera.image.colours :as colours]))

(defonce raw-data
  (with-open [reader (clojure.java.io/reader "vaki2016_1km_kp.csv")]
    (let [rows (csv/read-csv reader)]
      (mapv zipmap
            (->> (first rows)
                 (map keyword)
                 repeat)
            (rest rows)))))

(defonce data
  (map (fn [{:keys [xkoord ykoord kunta vaesto]}]
         {:x (Integer/parseInt xkoord)
          :y (Integer/parseInt ykoord)
          :kunta (Integer/parseInt kunta)
          :lkm (Integer/parseInt vaesto)})
       raw-data))

(defonce data-x-ordered
  (sort-by :x data))

(defonce data-y-ordered
  (sort-by :y data))

(defn- square [x]
  (* x x))

(defn distance-squared [a b]
  (+ (square (- (:x b)
                (:x a)))
     (square (- (:y b)
                (:y a)))))

(defn l1-distance [a b]
  (+ (m/abs (- (:x b)
               (:x a)))
     (m/abs (- (:y b)
               (:y a)))))

(defn closest
  ([point means]
   (closest point means distance-squared))
  ([point means distance-fn]
   (->> means
        (map (fn [mean]
               {:mean mean, :dist (distance-fn point mean)}))
        (sort-by :dist)
        first
        :mean)))

(defn weighted-average [values weights]
  (/ (reduce + (map * weights values))
     (reduce + weights)))

(defn mean-of-points [points]
  {:x (weighted-average (map :x points)
                        (map :lkm points))
   :y (weighted-average (map :y points)
                        (map :lkm points))})

(defn weighted-median [values weights]
  (let [middle-index (/ (reduce + weights) 2)
        cumulative-weights (reductions + weights)]
    (->> (map vector values cumulative-weights)
         (filter #(>= (second %) middle-index))
         first
         first)))

(defn median-of-points [points]
  (let [x-ordered (filter (set points)
                          data-x-ordered)
        y-ordered (filter (set points)
                          data-y-ordered)]
    {:x (weighted-median (map :x x-ordered)
                         (map :lkm x-ordered))
     :y (weighted-median (map :y y-ordered)
                         (map :lkm y-ordered))}))

(defn random-init-means [data n]
  (->> data
       shuffle
       (take n)
       set))

(defn kmeans* [data n distance-fn mean-fn]
  (time
   (loop [means (random-init-means data n)]
     (let [clusters (group-by #(closest % means distance-fn) data)
           new-means (->> (vals clusters)
                          (map mean-fn)
                          set)]
       (if (= means new-means)
         (map (fn [{:keys [x y]}] {:x (double x), :y (double y)}) means)
         (recur new-means))))))

(defn kmeans
  ([n]
   (kmeans data n))
  ([data n]
   (kmeans* data n distance-squared mean-of-points)))

(defn kmedians
  ([n]
   (kmedians data n))
  ([data n]
   (kmeans* data n l1-distance median-of-points)))


(defn -main
  [n output-file & [mean-or-median?]]
  (with-open [writer (clojure.java.io/writer output-file)]
    (csv/write-csv writer
                   (->> ((if (= mean-or-median? "median")
                           (do (println "median") kmedians)
                           (do (println "mean") kmeans))
                         (Integer/parseInt n))
                        (map #(vector (:x %) (:y %)))))))
