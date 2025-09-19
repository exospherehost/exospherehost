import { z, ZodTypeAny, ZodObject } from 'zod';

export abstract class BaseNode<I extends ZodTypeAny = ZodObject<any>, O extends ZodTypeAny = ZodObject<any>, S extends ZodTypeAny = ZodObject<any>> {
  static Inputs: ZodTypeAny = z.object({});
  static Outputs: ZodTypeAny = z.object({});
  static Secrets: ZodTypeAny = z.object({});

  protected inputs!: z.infer<I>;
  protected secrets!: z.infer<S>;

  constructor() {
    if (this.constructor === BaseNode) {
      throw new Error('BaseNode is an abstract class and cannot be instantiated directly');
    }
  }

  async _execute(inputsRaw: unknown, secretsRaw: unknown): Promise<z.infer<O> | z.infer<O>[]> {
    const ctor = this.constructor as typeof BaseNode;
    const inputs = (ctor.Inputs as I).parse(inputsRaw);
    const secrets = (ctor.Secrets as S).parse(secretsRaw);
    this.inputs = inputs;
    this.secrets = secrets;
    const result = await this.execute();
    const outputsSchema = ctor.Outputs as O;
    if (Array.isArray(result)) {
      return result.map(r => outputsSchema.parse(r));
    }
    if (result === null) {
      return null as any;
    }
    return outputsSchema.parse(result);
  }

  abstract execute(): Promise<z.infer<O> | z.infer<O>[]>;
}

