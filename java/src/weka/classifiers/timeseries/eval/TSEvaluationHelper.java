/*
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

/*
 * TSEvaluationHelper.java
 * Copyright (C) 2021 Fracpete (pythonwekawrapper at gmail dot com)
 */

package weka.classifiers.timeseries.eval;

import java.lang.reflect.Constructor;
import weka.core.Instances;
import weka.core.WekaPackageClassLoaderManager;

public class TSEvaluationHelper {

  /**
   * Creates a new instance of a TSEvaluationExt class.
   *
   * @param trainingData the training data to initialize with
   * @param testSplitSize the number of instances or percentage for the test set
   * @return the TSEvaluation instance
   */
  public static Object newInstance(Instances trainingData, double testSplitSize) {
    try {
      Class cls = WekaPackageClassLoaderManager.forName("weka.classifiers.timeseries.eval.TSEvaluation");
      Constructor constr = cls.getConstructor(Instances.class, Double.TYPE);
      return constr.newInstance(trainingData, testSplitSize);
    }
    catch (Exception e) {
      System.err.println("Failed to initialize TSEvaluation object:");
      e.printStackTrace();
      return null;
    }
  }

  /**
   * Creates a new instance of a TSEvaluationExt class.
   *
   * @param trainingData the training data to initialize with
   * @param testData the test data to initialize with
   * @return the TSEvaluation instance
   */
  public static Object newInstance(Instances trainingData, Instances testData) {
    try {
      Class cls = WekaPackageClassLoaderManager.forName("weka.classifiers.timeseries.eval.TSEvaluation");
      Constructor constr = cls.getConstructor(Instances.class, Instances.class);
      return constr.newInstance(trainingData, testData);
    }
    catch (Exception e) {
      System.err.println("Failed to initialize TSEvaluation object:");
      e.printStackTrace();
      return null;
    }
  }
}
