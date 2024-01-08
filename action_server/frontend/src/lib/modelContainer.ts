import { Dispatch } from 'react';

export enum ModelType {
  RUNS = 'runs',
  ACTIONS = 'actions',
}

export interface CachedModel<T> {
  isPending: boolean;
  data: T[] | undefined;
  errorMessage?: string | undefined;
}

export class ModelContainer {
  private models: Map<ModelType, CachedModel<unknown>>;

  private callbacks: Map<ModelType, Dispatch<unknown>[]>;

  constructor() {
    this.models = new Map();
    this.callbacks = new Map();

    this.models.set(ModelType.RUNS, {
      isPending: true,
      data: undefined,
    });
    this.models.set(ModelType.ACTIONS, {
      isPending: true,
      data: undefined,
    });
  }

  /**
   * This method should be called to start listening for changes in the model.
   * If the model is already loaded at this point it's colled for it
   *
   * @param type the model that should be listened.
   * @param callback A Dispatch<any> to be called when the model changes.
   */
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  public addListener(type: ModelType, callback: Dispatch<any>): void {
    let callbackList = this.callbacks.get(type);
    if (callbackList === undefined) {
      callbackList = [];
      this.callbacks.set(type, callbackList);
    }
    callbackList.push(callback);

    // If there's some model already loaded, call it right away with that model.
    const currentModel = this.models.get(type);
    if (currentModel !== undefined) {
      callback(currentModel);
    }
  }

  /**
   * Removes a callback that was previously listening to changes in the model.
   *
   * @param type the model that should no longer be listened by this Dispatch<any>
   * @param callback the previously registered callback.
   */
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  public removeListener(type: ModelType, callback: Dispatch<any>): void {
    const callbackList = this.callbacks.get(type);
    if (callbackList !== undefined) {
      const index = callbackList.indexOf(callback);
      if (index !== -1) {
        callbackList.splice(index, 1);
      }
    }
  }

  /**
   * Should be called when a new model is loaded from the backend.
   * It must be always set as a whole.
   */
  public onModelUpdated<T>(type: ModelType, model: CachedModel<T>): void {
    this.models.set(type, model);

    const callbacks = this.callbacks.get(type);
    if (callbacks !== undefined) {
      callbacks.forEach((callback) => callback(model));
    }
  }

  public getCurrentModel<T>(type: ModelType) {
    return this.models.get(type) as CachedModel<T> | undefined;
  }
}
