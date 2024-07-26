//Tests for the file auth.ts
import { execSync } from 'child_process';
import { login, register, getSalt } from '../content/auth';
import { User } from '../content/user';
import { LocalStorageHelper } from '../content/localStorageHelper'
import { genSaltSync } from 'bcryptjs-react';

describe("Auth.ts file tests", () => {
  beforeAll(() => {
    // clear our db
    execSync('buildjobrater', { stdio: 'inherit' });
  });
  it("Tests that we can properly talk to our auth server to get salt", () => {
    return expect(getSalt("dandemoney@gmail")).rejects.toMatch("");
  })
  it("Tests that we can properly register a user", () => {
    const mockUser : User = new User("_", "dandemoney@gmail.com", null, "Daniel", "DeMoney", null);
    return expect(register(mockUser, "Xdfgh1012#", "Xdfgh1012#", genSaltSync())).resolves.toMatch("Success");
  })
  it("Tests that we can login the user we just registered", async () => {
    await getSalt("dandemoney@gmail.com")
    .then((salt) => {
      return expect(login("dandemoney@gmail.com", "Xdfgh1012#", salt)).resolves.toBe("Success");
    })
  })
  it("Tests that we cannot login the user we just registered with a bad pw", async () => {
    await getSalt("dandemoney@gmail.com")
    .then((salt) => {
      return expect(login("dandemoney@gmail.com", "Xdfgh1012", salt)).rejects.toBe("401");
    })
  })
  it("Tests that we cannot register a duplicate user", () => {
    const mockUser : User = new User("_", "dandemoney@gmail.com", null, "Daniel", "DeMoney", null);
    return expect(register(mockUser, "Xdfgh1012#", "Xdfgh1012#", genSaltSync())).rejects.toBe("401");
  })
})