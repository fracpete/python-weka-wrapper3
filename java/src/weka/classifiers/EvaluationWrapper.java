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
 * EvaluationWrapper.java
 * Copyright (C) 2014 Fracpete (pythonwekawrapper at gmail dot com)
 */

package weka.classifiers;

import weka.core.Instances;

/**
 * Wrapper class without the "throws Exception" clause in the constructor.
 *
 * @author FracPete (pythonwekawrapper at gmail dot com)
 */
public class EvaluationWrapper {

  /** the wrapped evaluation object. */
  protected Evaluation m_Evaluation;

  /**
   * Initializes the wrapper.
   *
   * @param data the data to initialize with
   */
  public EvaluationWrapper(Instances data) {
    try {
      m_Evaluation = new Evaluation(data);
    }
    catch (Exception e) {
      System.err.println("Failed to initialize Evaluation object:");
      e.printStackTrace();
      m_Evaluation = null;
    }
  }

  /**
   * Initializes the wrapper.
   *
   * @param data the data to initialize with
   * @param matrix the cost matrix to initialize with
   */
  public EvaluationWrapper(Instances data, CostMatrix costMatrix) {
    try {
      m_Evaluation = new Evaluation(data, costMatrix);
    }
    catch (Exception e) {
      System.err.println("Failed to initialize Evaluation object:");
      e.printStackTrace();
      m_Evaluation = null;
    }
  }

  /**
   * Returns the wrapped evaluation object.
   *
   * @return the evaluation object or null if initialization failed
   */
  public Evaluation getEvaluation() {
    return m_Evaluation;
  }
}
