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
 * PickleHelper.java
 * Copyright (C) 2021 Fracpete (pythonwekawrapper at gmail dot com)
 */

package weka.core;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.ObjectOutputStream;

/**
 * Helper class for serialization objects to/fro byte arrays.
 *
 * @author FracPete (pythonwekawrapper at gmail dot com)
 */
public class PickleHelper {

  /**
   * Serializes the given object into a byte array.
   *
   * @param os		the objects to serialize
   * @return		the byte array
   * @throws Exception	if serialization fails
   */
  public static byte[] toByteArray(Object[] os) throws Exception {
    ByteArrayOutputStream	bos;
    ObjectOutputStream		oos;

    bos = new ByteArrayOutputStream();
    oos = new ObjectOutputStream(bos);
    try {
      for (Object o : os)
        oos.writeObject(o);
    }
    finally {
      if (oos != null) {
        try {
          oos.flush();
        }
        catch (Exception e) {
          // ignored
        }
        try {
          oos.close();
        }
        catch (Exception e) {
          // ignored
        }
      }
    }

    return bos.toByteArray();
  }

  /**
   * Deserializes from the given byte array and returns the objects from it.
   *
   * @param data	the byte array to deserialize from
   * @return		the deserialized objects
   * @throws Exception	if deserialization fails
   */
  public static Object[] fromByteArray(byte[] data) throws Exception {
    return SerializationHelper.readAll(new ByteArrayInputStream(data));
  }
}
